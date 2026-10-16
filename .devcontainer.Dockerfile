FROM mcr.microsoft.com/devcontainers/base:debian

# Optional: trust extra root certificates (e.g. a corporate TLS-inspecting proxy).
# Put *.crt files (PEM format) into .devcontainer-certs/; they are git-ignored.
COPY .devcontainer-certs/ /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates

# Make Python tooling use the system certificate store. Home Assistant installs
# integration requirements at runtime with uv, which ignores it unless told to.
ENV UV_NATIVE_TLS=1 \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt
