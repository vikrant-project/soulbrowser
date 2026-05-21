FROM python:3.12-slim

# Chromium system deps + Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdbus-1-3 libdrm2 libxkbcommon0 libatspi2.0-0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 libx11-xcb1 libfontconfig1 libx11-6 \
    libxcb1 libxext6 libxshmfence1 \
    libglib2.0-0 libgtk-3-0 libpangocairo-1.0-0 libcairo-gobject2 \
    libgdk-pixbuf-2.0-0 libxss1 libxtst6 fonts-liberation \
    fonts-noto-color-emoji fonts-unifont fonts-freefont-ttf \
    fonts-ipafont-gothic fonts-wqy-zenhei fonts-tlwg-loma-otf \
    xvfb xdotool \
    curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python wrapper
COPY pyproject.toml README.md LICENSE BINARY-LICENSE.md CHANGELOG.md ./
COPY soulbrowser/ soulbrowser/
RUN pip install --no-cache-dir ".[serve,geoip]"

# JS wrapper
COPY js/ js/
RUN cd js && npm install && npm run build

# Examples
COPY examples/ examples/

# Pre-download stealth Chromium binary during build (not at runtime)
# Remove welcome marker so users see it on first container run
RUN python -c "from soulbrowser import ensure_binary; ensure_binary()" \
    && rm -f ~/.soulbrowser/.welcome_shown

# CLI shortcuts
COPY bin/soultest /usr/local/bin/soultest
COPY bin/soulserve /usr/local/bin/soulserve
RUN chmod +x /usr/local/bin/soultest /usr/local/bin/soulserve

EXPOSE 9222

# Xvfb entrypoint for headed mode support
COPY bin/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DISPLAY=:99

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python"]
