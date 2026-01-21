# Wargame Sandbox - Ambiente isolado para simulações
# Build: docker build -t wargame-sandbox:latest -f docker/wargame-sandbox/Dockerfile .

FROM mcr.microsoft.com/powershell:7.4-ubuntu-22.04

# Metadados
LABEL maintainer="vertice-cyber"
LABEL description="Sandbox isolado para execução de wargames"

# Variáveis
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Criar usuário não-root
RUN groupadd -r wargame && useradd -r -g wargame wargame

# Instalar Python 3.12 e dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app
RUN chown wargame:wargame /app

# Instalar Atomic Red Team (PowerShell)
RUN pwsh -c "Install-Module -Name invoke-atomicredteam -Force -Scope AllUsers"
RUN pwsh -c "Install-Module -Name powershell-yaml -Force -Scope AllUsers"

# Baixar atomics (técnicas MITRE)
RUN git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git /opt/atomic-red-team

# Instalar dependências Python
COPY requirements-wargame.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements-wargame.txt

# Configurar permissões
RUN chmod -R 755 /opt/atomic-red-team

# Trocar para usuário não-root
USER wargame

# Comando padrão
CMD ["pwsh", "-NoProfile"]
