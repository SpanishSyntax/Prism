{
  description = "Rime - Crystalline Zero-Dependency Terminal UI, Panels & Interactive Menu Engine";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }: let
    systems = flake-utils.lib.defaultSystems;
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = import nixpkgs {inherit system;};
      lib = pkgs.lib;

      rimePackage = pkgs.python3Packages.buildPythonPackage {
        pname = "rime";
        version = "0.1.0";
        src = ./.;
        pyproject = true;

        build-system = [
          pkgs.python3Packages.setuptools
        ];

        nativeCheckInputs = [
          pkgs.python3Packages.pytest
        ];

        doCheck = false;

        meta = with lib; {
          description = "Crystalline zero-dependency terminal UI, ANSI styling, panels, and interactive menu engine";
          homepage = "https://github.com/SpanishSyntax/Rime";
          license = licenses.mit;
          mainProgram = "rime";
        };
      };
    in {
      packages = {
        default = rimePackage;
        rime = rimePackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${rimePackage}/bin/rime";
        };
        rime = {
          type = "app";
          program = "${rimePackage}/bin/rime";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3Packages.setuptools
          python3Packages.pytest
          rimePackage
        ];
      };
    })
    // {
      overlays = {
        default = final: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (pyFinal: pyPrev: {
              rime = pyFinal.buildPythonPackage {
                pname = "rime";
                version = "0.1.0";
                src = self;
                pyproject = true;
                build-system = [pyFinal.setuptools];
                nativeCheckInputs = [pyFinal.pytest];
                doCheck = false;
              };
            })
          ];
          rime = self.packages.${prev.stdenv.hostPlatform.system}.default;
        };
        rime = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.rime;
        rime = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.rime;
          system = pkgs.stdenv.hostPlatform.system;
        in {
          options.programs.rime = {
            enable = lib.mkEnableOption "Rime - Crystalline terminal UI toolkit";
            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${system}.default;
              description = "The Rime package to install.";
            };
          };
          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
      };

      homeManagerModules = {
        default = self.homeManagerModules.rime;
        rime = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.rime;
          system = pkgs.stdenv.hostPlatform.system;
        in {
          options.programs.rime = {
            enable = lib.mkEnableOption "Rime - Crystalline terminal UI toolkit";
            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${system}.default;
              description = "The Rime package to install.";
            };
          };
          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];
          };
        };
      };
    };
}
