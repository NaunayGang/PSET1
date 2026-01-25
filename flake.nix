{
  description = "PSET1: Demand Prediction Service with Nix devShell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pandoc-resources = {
      url = "github:yuuhikaze/pandoc-resources";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, pandoc-resources, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          fastapi
          streamlit
          pandas
          pyarrow
          uvicorn
          requests
          pytest
          httpx
        ]);

        tern = pkgs.stdenv.mkDerivation {
          pname = "tern";
          version = "1.7.0";
          src = pkgs.fetchurl {
            url = "https://github.com/yuuhikaze/tern/releases/download/v1.7.0/tern";
            sha256 = "8513e762741ca4538f1d42bf9bd43d52a3019b393b36e6a19cd1790a773fbd7f";
          };
          phases = [ "installPhase" ];
          installPhase = ''
            mkdir -p $out/bin
            cp $src $out/bin/tern
            chmod +x $out/bin/tern
          '';
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.docker
            pkgs.docker-compose
            pkgs.git
            pkgs.pandoc
            tern
          ] ++ (with pkgs; [
            fontconfig
            wayland
            libxkbcommon
            libGL
            xorg.libX11
            xorg.libXcursor
            xorg.libXrandr
            xorg.libXi
          ]);

          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath (with pkgs; [
              wayland
              libxkbcommon
              xorg.libX11
              xorg.libXcursor
              xorg.libXrandr
              xorg.libXi
              fontconfig
              libGL
            ])}

            # Setup Tern Converter
            mkdir -p ~/.local/share/tern/converters
            ln -sf ${pandoc-resources}/tern-converters/pandoc.lua ~/.local/share/tern/converters/pandoc.lua

            # Setup Pandoc Templates
            mkdir -p ~/.local/share/pandoc/templates
            ln -sf ${pandoc-resources}/pandoc-templates/docs.html ~/.local/share/pandoc/templates/docs.html
            ln -sf ${pandoc-resources}/pandoc-templates/docs.css ~/.local/share/pandoc/templates/docs.css

            # export PANDOC_DOCS_HTML="$HOME/.local/share/pandoc/templates/docs.html"
            # ts one is needed bc pandoc for some reason does not "add to path" CSS templates
            export PANDOC_DOCS_CSS="$HOME/.local/share/pandoc/templates/docs.css"
            # basic usage: pandoc -f markdown --template='docs.html' --mathjax --embed-resources --css="$PANDOC_DOCS_CSS" -t html -i <input.md> -o <output.html>

            echo "======= PSET1 Development Environment ======="
            echo "Python: $(python --version)"
            echo "Docker: $(docker --version)"
            echo "Tern:   $(tern --version)"
            echo "Pandoc: $(pandoc --version | head -n 1)"
            echo "Resources synced ✓"
            echo "============================================="
          '';
        };
      }
    );
}
