{
  description = "Prism - Crystalline Zero-Dependency Terminal UI, Panels & Interactive Menu Engine";

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

      prismPackage = pkgs.python3Packages.buildPythonPackage {
        pname = "prism";
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
          homepage = "https://github.com/SpanishSyntax/Prism";
          license = licenses.mit;
          mainProgram = "prism";
        };
      };
    in {
      packages = {
        default = prismPackage;
        prism = prismPackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${prismPackage}/bin/prism";
        };
        prism = {
          type = "app";
          program = "${prismPackage}/bin/prism";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3Packages.setuptools
          python3Packages.pytest
          prismPackage
        ];
      };
    })
    // {
      overlays = {
        default = final: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (pyFinal: pyPrev: {
              prism = pyFinal.buildPythonPackage {
                pname = "prism";
                version = "0.1.0";
                src = self;
                pyproject = true;
                build-system = [pyFinal.setuptools];
                nativeCheckInputs = [pyFinal.pytest];
                doCheck = false;
              };
            })
          ];
          prism = self.packages.${prev.stdenv.hostPlatform.system}.default;
        };
        prism = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.prism;
        prism = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.prism;
          system = pkgs.stdenv.hostPlatform.system;
        in {
          options.programs.prism = {
            enable = lib.mkEnableOption "Prism - Crystalline terminal UI toolkit";
            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${system}.default;
              description = "The Prism package to install.";
            };
          };
          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
      };

      homeManagerModules = {
        default = self.homeManagerModules.prism;
        prism = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.prism;
          system = pkgs.stdenv.hostPlatform.system;
        in {
          options.programs.prism = {
            enable = lib.mkEnableOption "Prism - Crystalline terminal UI toolkit";
            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${system}.default;
              description = "The Prism package to install.";
            };
          };
          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];
          };
        };
      };
    };
}
