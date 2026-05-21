{
  description = "SoulBrowser development shell with Nix-packaged Chromium binaries";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      inherit (nixpkgs) lib;

      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      forAllSystems = lib.genAttrs supportedSystems;

      packageInfo = {
        x86_64-linux = {
          platformTag = "linux-x64";
          version = "146.0.7680.177.5";
          hash = "sha256-ShK83pX6G7G+7ytBq15cJ8Nr544749DayMZNcFIWZw4=";
        };
        aarch64-linux = {
          platformTag = "linux-arm64";
          version = "146.0.7680.177.3";
          hash = "sha256-i3HOU7T9ExMnMxox+6ODXXGILRm/qr3njdD1OQvRb0U=";
        };
      };

      soulbrowserBinaryLicense = {
        shortName = "soulbrowser-binary";
        fullName = "SoulBrowser Binary License";
        url = "https://github.com/CloakHQ/SoulBrowser/blob/main/BINARY-LICENSE.md";
        free = false;
        redistributable = false;
      };

      mkPkgs = system: import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };

      runtimeLibraries = pkgs: with pkgs; [
        alsa-lib
        at-spi2-atk
        at-spi2-core
        atk
        cairo
        cups
        dbus
        expat
        fontconfig
        freetype
        gdk-pixbuf
        glib
        gtk3
        libdrm
        libgbm
        libGL
        libpulseaudio
        libxkbcommon
        mesa
        nspr
        nss
        pango
        systemd
        wayland
        libx11
        libxcb
        libxcomposite
        libxcursor
        libxdamage
        libxext
        libxfixes
        libxi
        libxrandr
        libxrender
        libxscrnsaver
        libxshmfence
        libxtst
      ];

      fontPackages = pkgs: with pkgs; [
        freefont_ttf
        ipafont
        liberation_ttf
        noto-fonts
        noto-fonts-cjk-sans
        noto-fonts-color-emoji
        tlwg
        unifont
        wqy_zenhei
      ];

      desktopPackages = pkgs: with pkgs; [
        adwaita-icon-theme
        gsettings-desktop-schemas
        xdg-utils
      ];

      mkSoulBrowserChromium = pkgs: system:
        let
          info = packageInfo.${system} or (throw "SoulBrowser flake package currently supports only x86_64-linux and aarch64-linux.");
          archiveName = "soulbrowser-${info.platformTag}.tar.gz";
          chromiumVersion = info.version;
          libs = runtimeLibraries pkgs;
          desktopDeps = desktopPackages pkgs;
          fonts = fontPackages pkgs;
          fontsConf = pkgs.makeFontsConf {
            fontDirectories = fonts;
          };
        in
        pkgs.stdenvNoCC.mkDerivation {
          pname = "soulbrowser-chromium";
          version = chromiumVersion;

          src = pkgs.fetchurl {
            url = "https://soulbrowser.dev/chromium-v${chromiumVersion}/${archiveName}";
            inherit (info) hash;
          };

          dontUnpack = true;

          nativeBuildInputs = with pkgs; [
            autoPatchelfHook
            makeWrapper
          ];

          buildInputs = libs ++ desktopDeps;
          runtimeDependencies = libs;

          installPhase = ''
            runHook preInstall

            mkdir -p "$out/lib/soulbrowser" "$out/bin"
            tar -xzf "$src" -C "$out/lib/soulbrowser"
            chmod +x "$out/lib/soulbrowser/chrome"
            chmod +x "$out/lib/soulbrowser/chromedriver"

            runHook postInstall
          '';

          postFixup = ''
            makeWrapper "$out/lib/soulbrowser/chrome" "$out/bin/soulbrowser-chrome" \
              --prefix LD_LIBRARY_PATH : "${lib.makeLibraryPath libs}" \
              --prefix XDG_DATA_DIRS : "$GSETTINGS_SCHEMAS_PATH:$XDG_ICON_DIRS" \
              --suffix PATH : "${lib.makeBinPath [ pkgs.xdg-utils ]}" \
              --set FONTCONFIG_FILE "${fontsConf}" \
              --set CHROME_WRAPPER "soulbrowser-chrome"

            makeWrapper "$out/lib/soulbrowser/chromedriver" "$out/bin/soulbrowser-chromedriver" \
              --prefix LD_LIBRARY_PATH : "${lib.makeLibraryPath libs}"
          '';

          meta = {
            description = "Official SoulBrowser patched Chromium binary";
            homepage = "https://github.com/CloakHQ/SoulBrowser";
            license = soulbrowserBinaryLicense;
            mainProgram = "soulbrowser-chrome";
            platforms = supportedSystems;
            sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
          };
        };
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = mkPkgs system;
          soulbrowserChromium = mkSoulBrowserChromium pkgs system;
        in
        {
          inherit soulbrowserChromium;
          default = soulbrowserChromium;
        });

      apps = forAllSystems (system:
        let
          soulbrowserChromium = self.packages.${system}.soulbrowserChromium;
        in
        {
          default = {
            type = "app";
            program = "${soulbrowserChromium}/bin/soulbrowser-chrome";
            meta.description = "Run SoulBrowser Chromium";
          };
          soulbrowser-chrome = {
            type = "app";
            program = "${soulbrowserChromium}/bin/soulbrowser-chrome";
            meta.description = "Run SoulBrowser Chromium";
          };
          soulbrowser-chromedriver = {
            type = "app";
            program = "${soulbrowserChromium}/bin/soulbrowser-chromedriver";
            meta.description = "Run the SoulBrowser Chromedriver binary";
          };
        });

      devShells = forAllSystems (system:
        let
          pkgs = mkPkgs system;
          soulbrowserChromium = self.packages.${system}.soulbrowserChromium;
          python = pkgs.python312.withPackages (ps: with ps; [
            aiohttp
            geoip2
            hatchling
            httpx
            playwright
            pytest
            pytest-asyncio
            socksio
            websockets
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [
              soulbrowserChromium
              python
              pkgs.cacert
              pkgs.curl
              pkgs.git
              pkgs.jq
              pkgs.nodejs_20
              pkgs.which
              pkgs.xdotool
              pkgs.xvfb-run
            ]
            ++ runtimeLibraries pkgs
            ++ fontPackages pkgs;

            SOULBROWSER_BINARY_PATH = "${soulbrowserChromium}/bin/soulbrowser-chrome";
          };
        });
    };
}
