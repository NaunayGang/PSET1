{
  description = "PSET1: Demand Prediction Service with Nix devShell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
    tern-src = {
      url = "github:yuuhikaze/tern";
    };
    pandoc-resources = {
      url = "github:yuuhikaze/pandoc-resources";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay, tern-src, pandoc-resources, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
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

        tern-core = tern-src.packages.${system}.tern-core;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.docker
            pkgs.docker-compose
            pkgs.git
            pkgs.pandoc
            tern-core
          ];

          shellHook = ''
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
            echo "Tern:   $(tern-core --version)"
            echo "Pandoc: $(pandoc --version | head -n 1)"
            echo "Resources synced ✓"
            echo "============================================="
          '';
        };
      }
    );
}
