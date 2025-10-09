#!/usr/bin/env python3
"""
CLI para Agents Upstream - Sistema de análise de pesquisa com agentes especializados de IA.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple


class Colors:
    """Cores ANSI para terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'


def print_banner():
    """Exibe o banner do Agents Upstream"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🤖  AGENTS UPSTREAM  🤖                          ║
║                                                               ║
║     Sistema de Análise de Pesquisa com Agentes de IA         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)


def get_template_dir() -> Path:
    """Obtém o diretório dos templates no pacote"""
    # O template está na mesma pasta do pacote
    package_dir = Path(__file__).parent
    template_dir = package_dir / "templates"
    
    if not template_dir.exists():
        print(f"{Colors.RED}❌ Erro: Diretório de templates não encontrado!{Colors.RESET}")
        sys.exit(1)
    
    return template_dir


def copy_templates(destination: Path) -> bool:
    """
    Copia os templates para o diretório de destino
    
    Args:
        destination: Diretório de destino
        
    Returns:
        True se bem-sucedido, False caso contrário
    """
    try:
        template_dir = get_template_dir()
        
        print(f"\n{Colors.BLUE}📦 Copiando templates e agentes...{Colors.RESET}")
        
        # Copiar estrutura de templates
        for item in template_dir.iterdir():
            dest_path = destination / item.name
            
            if item.is_dir():
                if dest_path.exists():
                    print(f"{Colors.YELLOW}⚠️  Pasta {item.name} já existe, pulando...{Colors.RESET}")
                else:
                    shutil.copytree(item, dest_path)
                    print(f"{Colors.GREEN}✓{Colors.RESET} Copiado: {item.name}/")
            else:
                if dest_path.exists():
                    print(f"{Colors.YELLOW}⚠️  Arquivo {item.name} já existe, pulando...{Colors.RESET}")
                else:
                    shutil.copy2(item, dest_path)
                    print(f"{Colors.GREEN}✓{Colors.RESET} Copiado: {item.name}")
        
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao copiar templates: {e}{Colors.RESET}")
        return False


def show_next_steps():
    """Exibe os próximos passos após a instalação"""
    next_steps = f"""
{Colors.GREEN}{Colors.BOLD}✨ Instalação concluída com sucesso!{Colors.RESET}

{Colors.CYAN}{Colors.BOLD}📋 PRÓXIMOS PASSOS:{Colors.RESET}

{Colors.BOLD}1. Preparar materiais de pesquisa:{Colors.RESET}
   • Coloque arquivos de entrevista em: {Colors.YELLOW}0-documentation/0b-Interviews/{Colors.RESET}
   • Atualize o contexto em: {Colors.YELLOW}0-documentation/0a-projectdocs/context.md{Colors.RESET}

{Colors.BOLD}2. Iniciar workflow no Cursor AI:{Colors.RESET}
   Digite: {Colors.YELLOW}start workflow{Colors.RESET}

{Colors.BOLD}3. Documentação completa:{Colors.RESET}
   Consulte: {Colors.YELLOW}README.md{Colors.RESET} no diretório atual

{Colors.CYAN}{Colors.BOLD}📚 Estrutura criada:{Colors.RESET}
   • 0-documentation/          (Contexto do projeto)
   • _output-structure/        (Templates de análise)
   • .cursor/rules/            (Agentes de IA)

{Colors.GREEN}Permite que equipes de produto pensem estrategicamente sem sacrificar velocidade.{Colors.RESET}
"""
    print(next_steps)


def is_directory_empty(directory: Path) -> bool:
    """Verifica se o diretório está vazio (ignora arquivos ocultos)"""
    try:
        items = [f for f in directory.iterdir() if not f.name.startswith('.')]
        return len(items) == 0
    except:
        return True


def get_user_bin_path() -> Path:
    """Obtém o diretório de scripts do usuário"""
    if platform.system() == "Windows":
        # Windows: %APPDATA%\Python\PythonXX\Scripts
        python_version = f"Python{sys.version_info.major}{sys.version_info.minor}"
        return Path(os.environ.get('APPDATA', '')) / python_version / 'Scripts'
    else:
        # Linux/Mac: ~/.local/bin
        return Path.home() / '.local' / 'bin'


def is_in_path(directory: Path) -> bool:
    """Verifica se o diretório está no PATH"""
    path_env = os.environ.get('PATH', '')
    path_dirs = path_env.split(os.pathsep)
    return str(directory) in path_dirs or str(directory.resolve()) in path_dirs


def get_shell_config_file() -> Optional[Path]:
    """Detecta o arquivo de configuração do shell"""
    shell = os.environ.get('SHELL', '')
    home = Path.home()
    
    if 'zsh' in shell:
        return home / '.zshrc'
    elif 'bash' in shell:
        # Verificar se está no Mac ou Linux
        if platform.system() == 'Darwin':
            bash_profile = home / '.bash_profile'
            if bash_profile.exists():
                return bash_profile
        return home / '.bashrc'
    elif 'fish' in shell:
        return home / '.config' / 'fish' / 'config.fish'
    
    # Fallback: tentar detectar qual existe
    for config in [home / '.zshrc', home / '.bashrc', home / '.bash_profile']:
        if config.exists():
            return config
    
    # Padrão: usar .bashrc
    return home / '.bashrc'


def add_to_path_unix() -> Tuple[bool, str]:
    """Adiciona ~/.local/bin ao PATH no Unix/Mac"""
    try:
        user_bin = get_user_bin_path()
        config_file = get_shell_config_file()
        
        if not config_file:
            return False, "Não foi possível detectar o arquivo de configuração do shell"
        
        # Verificar se já está no arquivo de configuração
        if config_file.exists():
            content = config_file.read_text()
            if str(user_bin) in content or '$HOME/.local/bin' in content:
                return True, f"PATH já configurado em {config_file.name}"
        
        # Adicionar ao arquivo de configuração
        export_line = f'\n# Added by agents-upstream\nexport PATH="$HOME/.local/bin:$PATH"\n'
        
        with open(config_file, 'a') as f:
            f.write(export_line)
        
        return True, f"PATH adicionado a {config_file.name}. Execute: source {config_file}"
    
    except Exception as e:
        return False, f"Erro ao configurar PATH: {e}"


def add_to_path_windows() -> Tuple[bool, str]:
    """Adiciona o diretório de scripts ao PATH do usuário no Windows"""
    try:
        user_bin = get_user_bin_path()
        
        # Usar PowerShell para adicionar ao PATH do usuário
        ps_script = f"""
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$scriptsPath = "{user_bin}"
if ($userPath -notlike "*$scriptsPath*") {{
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$scriptsPath", "User")
    Write-Output "SUCCESS"
}} else {{
    Write-Output "ALREADY_EXISTS"
}}
"""
        
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout.strip()
        
        if output == "SUCCESS":
            return True, "PATH configurado! Reinicie o terminal para aplicar as mudanças."
        elif output == "ALREADY_EXISTS":
            return True, "PATH já estava configurado corretamente."
        else:
            return False, "Erro ao configurar PATH no Windows"
    
    except Exception as e:
        return False, f"Erro ao configurar PATH: {e}"


def check_and_offer_path_setup() -> None:
    """Verifica se o comando está no PATH e oferece configurar"""
    user_bin = get_user_bin_path()
    
    # Se o diretório não existe, não há necessidade de configurar ainda
    if not user_bin.exists():
        return
    
    # Verificar se já está no PATH
    if is_in_path(user_bin):
        return
    
    # PATH não está configurado - oferecer configuração automática
    print(f"\n{Colors.YELLOW}⚠️  ATENÇÃO: Configuração de PATH necessária{Colors.RESET}")
    print(f"\n{Colors.BOLD}Para usar o comando 'agents-upstream' de qualquer lugar, o diretório{Colors.RESET}")
    print(f"{Colors.CYAN}{user_bin}{Colors.RESET}")
    print(f"{Colors.BOLD}precisa estar no PATH do seu sistema.{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Opções:{Colors.RESET}")
    print(f"{Colors.GREEN}  1.{Colors.RESET} Configurar automaticamente (recomendado)")
    print(f"{Colors.CYAN}  2.{Colors.RESET} Pular e usar 'pipx run agents-upstream'")
    print(f"{Colors.YELLOW}  3.{Colors.RESET} Configurar manualmente depois\n")
    
    while True:
        choice = input(f"{Colors.BOLD}Escolha (1-3): {Colors.RESET}").strip()
        
        if choice == '1':
            print(f"\n{Colors.BLUE}🔧 Configurando PATH automaticamente...{Colors.RESET}")
            
            if platform.system() == "Windows":
                success, message = add_to_path_windows()
            else:
                success, message = add_to_path_unix()
            
            if success:
                print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
                if platform.system() != "Windows":
                    print(f"\n{Colors.YELLOW}💡 Para aplicar agora, execute:{Colors.RESET}")
                    config_file = get_shell_config_file()
                    if config_file:
                        print(f"{Colors.CYAN}   source {config_file}{Colors.RESET}")
                print()
            else:
                print(f"{Colors.RED}❌ {message}{Colors.RESET}")
                print(f"\n{Colors.YELLOW}Use 'pipx run agents-upstream' como alternativa.{Colors.RESET}\n")
            break
        
        elif choice == '2':
            print(f"\n{Colors.CYAN}💡 Use sempre: {Colors.YELLOW}pipx run agents-upstream{Colors.RESET}\n")
            break
        
        elif choice == '3':
            print(f"\n{Colors.YELLOW}📖 Consulte PATH_TROUBLESHOOTING.md para instruções manuais.{Colors.RESET}\n")
            break
        
        else:
            print(f"{Colors.RED}Opção inválida. Escolha 1, 2 ou 3.{Colors.RESET}")


def get_user_choice() -> str:
    """Obtém escolha do usuário quando o diretório não está vazio"""
    print(f"{Colors.YELLOW}✓ Pasta atual tem conteúdo existente{Colors.RESET}\n")
    print(f"{Colors.BOLD}Escolha uma opção:{Colors.RESET}")
    print(f"{Colors.CYAN}  1. {Colors.RESET}Criar em ./agents-upstream (recomendado)")
    print(f"{Colors.CYAN}  2. {Colors.RESET}Criar em ./[nome-customizado]")
    print(f"{Colors.YELLOW}  3. {Colors.RESET}Continuar na pasta atual ⚠️")
    print(f"{Colors.RED}  4. {Colors.RESET}Cancelar")
    
    while True:
        choice = input(f"\n{Colors.BOLD}Escolha (1-4): {Colors.RESET}").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print(f"{Colors.RED}Opção inválida. Por favor, escolha 1, 2, 3 ou 4.{Colors.RESET}")


def setup_path_command():
    """Comando para configurar PATH manualmente"""
    print_banner()
    print(f"{Colors.CYAN}{Colors.BOLD}🔧 Configuração de PATH{Colors.RESET}\n")
    
    user_bin = get_user_bin_path()
    
    if is_in_path(user_bin):
        print(f"{Colors.GREEN}✅ PATH já está configurado corretamente!{Colors.RESET}")
        print(f"{Colors.CYAN}   {user_bin}{Colors.RESET}")
        print(f"\nO comando 'agents-upstream' deve funcionar de qualquer diretório.\n")
        sys.exit(0)
    
    print(f"{Colors.YELLOW}O diretório de scripts não está no PATH:{Colors.RESET}")
    print(f"{Colors.CYAN}   {user_bin}{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Deseja configurar agora?{Colors.RESET}")
    print(f"{Colors.GREEN}  1.{Colors.RESET} Sim, configurar automaticamente")
    print(f"{Colors.YELLOW}  2.{Colors.RESET} Não, mostrar instruções manuais")
    print(f"{Colors.RED}  3.{Colors.RESET} Cancelar\n")
    
    while True:
        choice = input(f"{Colors.BOLD}Escolha (1-3): {Colors.RESET}").strip()
        
        if choice == '1':
            print(f"\n{Colors.BLUE}🔧 Configurando PATH...{Colors.RESET}")
            
            if platform.system() == "Windows":
                success, message = add_to_path_windows()
            else:
                success, message = add_to_path_unix()
            
            if success:
                print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
                if platform.system() != "Windows":
                    print(f"\n{Colors.YELLOW}💡 Para aplicar agora, execute:{Colors.RESET}")
                    config_file = get_shell_config_file()
                    if config_file:
                        print(f"{Colors.CYAN}   source {config_file}{Colors.RESET}")
                        print(f"\n{Colors.BOLD}Ou simplesmente reinicie o terminal.{Colors.RESET}\n")
                else:
                    print(f"\n{Colors.BOLD}Reinicie o terminal para aplicar as mudanças.{Colors.RESET}\n")
            else:
                print(f"{Colors.RED}❌ {message}{Colors.RESET}\n")
            
            sys.exit(0)
        
        elif choice == '2':
            print(f"\n{Colors.CYAN}{Colors.BOLD}📖 Instruções Manuais:{Colors.RESET}\n")
            
            if platform.system() == "Windows":
                print(f"{Colors.BOLD}Windows - PowerShell:{Colors.RESET}")
                print(f'{Colors.CYAN}$userPath = [Environment]::GetEnvironmentVariable("Path", "User"){Colors.RESET}')
                print(f'{Colors.CYAN}[Environment]::SetEnvironmentVariable("Path", "$userPath;{user_bin}", "User"){Colors.RESET}\n')
            else:
                config_file = get_shell_config_file()
                print(f"{Colors.BOLD}Linux/Mac - Adicione ao {config_file.name if config_file else '.bashrc'}:{Colors.RESET}")
                print(f'{Colors.CYAN}export PATH="$HOME/.local/bin:$PATH"{Colors.RESET}\n')
                print(f"{Colors.BOLD}Depois execute:{Colors.RESET}")
                if config_file:
                    print(f"{Colors.CYAN}source {config_file}{Colors.RESET}\n")
            
            sys.exit(0)
        
        elif choice == '3':
            print(f"\n{Colors.YELLOW}Configuração cancelada.{Colors.RESET}\n")
            sys.exit(0)
        
        else:
            print(f"{Colors.RED}Opção inválida. Escolha 1, 2 ou 3.{Colors.RESET}")


def main():
    """Função principal do CLI"""
    # Verificar se é comando --setup-path
    if len(sys.argv) > 1 and sys.argv[1] in ['--setup-path', '-p', 'setup-path']:
        setup_path_command()
        return
    
    # Verificar se é comando --help
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_banner()
        print(f"{Colors.CYAN}{Colors.BOLD}📖 Uso:{Colors.RESET}\n")
        print(f"{Colors.BOLD}agents-upstream{Colors.RESET}")
        print(f"  Instala templates e agentes no diretório atual\n")
        print(f"{Colors.BOLD}agents-upstream --setup-path{Colors.RESET}")
        print(f"  Configura o PATH para usar o comando globalmente\n")
        print(f"{Colors.BOLD}agents-upstream --help{Colors.RESET}")
        print(f"  Mostra esta mensagem de ajuda\n")
        sys.exit(0)
    
    print_banner()
    
    # Diretório atual
    current_dir = Path.cwd()
    target_dir = current_dir
    
    # Verificar se o diretório está vazio
    is_empty = is_directory_empty(current_dir)
    
    if not is_empty:
        choice = get_user_choice()
        
        if choice == '4':
            print(f"\n{Colors.RED}❌ Instalação cancelada.{Colors.RESET}\n")
            sys.exit(0)
        
        elif choice == '1':
            target_dir = current_dir / 'agents-upstream'
            if target_dir.exists():
                print(f"\n{Colors.RED}❌ A pasta \"agents-upstream\" já existe.{Colors.RESET}\n")
                sys.exit(1)
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n{Colors.GREEN}✓ Pasta criada: ./agents-upstream{Colors.RESET}\n")
        
        elif choice == '2':
            while True:
                folder_name = input(f"\n{Colors.BOLD}Digite o nome da pasta: {Colors.RESET}").strip()
                if not folder_name:
                    print(f"{Colors.RED}Por favor, digite um nome válido.{Colors.RESET}")
                    continue
                if '/' in folder_name or '\\' in folder_name:
                    print(f"{Colors.RED}O nome não pode conter barras.{Colors.RESET}")
                    continue
                
                target_dir = current_dir / folder_name
                if target_dir.exists():
                    print(f"\n{Colors.RED}❌ A pasta \"{folder_name}\" já existe.{Colors.RESET}\n")
                    sys.exit(1)
                
                target_dir.mkdir(parents=True, exist_ok=True)
                print(f"\n{Colors.GREEN}✓ Pasta criada: ./{folder_name}{Colors.RESET}\n")
                break
        
        elif choice == '3':
            print(f"\n{Colors.YELLOW}⚠️  Arquivos existentes podem ser sobrescritos.{Colors.RESET}\n")
    
    # Exibir diretório de instalação
    print(f"{Colors.BLUE}📁 Diretório de instalação: {Colors.BOLD}{target_dir}{Colors.RESET}\n")
    
    # Copiar templates
    if not copy_templates(target_dir):
        sys.exit(1)
    
    # Verificar e configurar PATH se necessário
    check_and_offer_path_setup()
    
    # Mostrar próximos passos
    show_next_steps()
    
    # Exibir comando cd se foi criada uma subpasta
    if target_dir != current_dir:
        print(f"\n{Colors.BLUE}📂 Arquivos instalados em: {Colors.CYAN}{target_dir.name}{Colors.RESET}")
        print(f"{Colors.BOLD}Execute: {Colors.RESET}cd {target_dir.name}\n")
    
    sys.exit(0)


if __name__ == "__main__":
    main()

