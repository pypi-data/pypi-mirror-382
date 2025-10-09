{
  description = "Red - a Reddit CLI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1.tar.gz";
    flakelight = {
      url = "github:nix-community/flakelight";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    devshell = {
      url = "github:numtide/devshell";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pre-commit = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      devshell,
      flakelight,
      nixpkgs,
      pre-commit,
      treefmt-nix,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }@inputs:
    flakelight ./. (
      { lib, ... }:
      let
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
        overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
        pythonSet =
          pkgs:
          (pkgs.callPackage pyproject-nix.build.packages { python = pkgs.python313; }).overrideScope (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
            ]
          );
        mkApplication = pkgs: (pkgs.callPackages pyproject-nix.build.util { }).mkApplication;
      in
      {
        inherit inputs;
        systems = [
          "aarch64-apple-darwin"
          "aarch64-darwin"
          "x86_64-linux"
        ];
        nixpkgs.config.allowUnfree = true;
        withOverlays = [ devshell.overlays.default ];

        package =
          { pkgs, ... }:
          let
            pySet = pythonSet pkgs;
          in
          mkApplication pkgs {
            venv = (pySet.mkVirtualEnv "red" workspace.deps.default).overrideAttrs (old: {
              passthru = lib.recursiveUpdate (old.passthru or { }) {
                inherit (pythonSet.testing.passthru) tests;
              };
              meta = (old.meta or { }) // {
                mainProgram = "red";
              };
            });
            package = pySet.red-reddit-cli;
          };

        app = pkgs: {
          type = "app";
          program = lib.getExe self.packages.${pkgs.system}.default;
        };

        devShell =
          pkgs:
          pkgs.devshell.mkShell {
            name = "red";

            packages = with pkgs; [
              act
              ruff
              uv
            ];
          };

        # evalModules here to pass eval'd config to formatting check below
        # so that nix flake check passes for formatting
        formatter =
          pkgs:
          with treefmt-nix.lib;
          let
            shInclude = [ ".envrc" ];
            inherit
              (evalModule pkgs {
                projectRootFile = "flake.nix";
                programs = {
                  mdformat.enable = true;
                  nixfmt.enable = true;
                  deadnix.enable = true;
                  prettier.enable = true;
                  ruff-check.enable = true;
                  ruff-format.enable = true;
                  statix.enable = true;
                  shellcheck = {
                    enable = true;
                    includes = shInclude;
                  };
                  shfmt = {
                    enable = true;
                    includes = shInclude;
                  };
                  yamlfmt = {
                    enable = true;
                    settings = {
                      gitignore_excludes = true;
                      formatter = {
                        include_document_start = true;
                        indent = 2;
                        max_line_length = 80;
                        pad_line_comments = 2;
                        retain_line_breaks_single = true;
                        scan_folded_as_literal = true;
                        trim_trailing_whitespace = true;
                        type = "basic";
                      };
                    };
                  };
                };
              })
              config
              ;
          in
          mkWrapper pkgs (
            config
            // {
              build.wrapper = pkgs.writeShellScriptBin "treefmt-nix" ''
                exec ${config.build.wrapper}/bin/treefmt --no-cache "$@"
              '';
            }
          );

        checks.formatting = lib.mkForce (
          { lib, outputs', ... }:
          ''
            ${lib.getExe outputs'.formatter} .
          ''
        );

        perSystem = pkgs: {
          checks.pre-commit = pre-commit.lib.${pkgs.system}.run {
            src = ./.;
            hooks = {
              nixfmt-rfc-style.enable = true;
              ruff.enable = true;
              ruff-format.enable = true;
            };
          };
        };
      }
    );
}
