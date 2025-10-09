#!/usr/bin/env python3
"""
CLI para Agents Upstream - Sistema de análise de pesquisa com agentes especializados de IA.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional


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


def main():
    """Função principal do CLI"""
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
    
    # Mostrar próximos passos
    show_next_steps()
    
    # Exibir comando cd se foi criada uma subpasta
    if target_dir != current_dir:
        print(f"\n{Colors.BLUE}📂 Arquivos instalados em: {Colors.CYAN}{target_dir.name}{Colors.RESET}")
        print(f"{Colors.BOLD}Execute: {Colors.RESET}cd {target_dir.name}\n")
    
    sys.exit(0)


if __name__ == "__main__":
    main()

