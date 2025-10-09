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


def create_cursor_rules(destination: Path) -> bool:
    """
    Cria o diretório .cursor/rules com os agentes
    
    Args:
        destination: Diretório de destino
        
    Returns:
        True se bem-sucedido, False caso contrário
    """
    try:
        cursor_dir = destination / ".cursor" / "rules"
        
        # O .cursor/rules está dentro do template
        template_cursor = get_template_dir() / ".cursor" / "rules"
        
        if not template_cursor.exists():
            print(f"{Colors.YELLOW}⚠️  Diretório .cursor/rules não encontrado nos templates{Colors.RESET}")
            return True
        
        if cursor_dir.exists():
            print(f"{Colors.YELLOW}⚠️  .cursor/rules já existe, pulando...{Colors.RESET}")
            return True
        
        print(f"\n{Colors.BLUE}🤖 Configurando agentes de IA...{Colors.RESET}")
        shutil.copytree(template_cursor, cursor_dir)
        print(f"{Colors.GREEN}✓{Colors.RESET} Agentes de IA configurados em .cursor/rules/")
        
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao criar .cursor/rules: {e}{Colors.RESET}")
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


def main():
    """Função principal do CLI"""
    print_banner()
    
    # Diretório de destino é o diretório atual
    destination = Path.cwd()
    
    print(f"{Colors.BLUE}📁 Diretório de instalação: {Colors.BOLD}{destination}{Colors.RESET}\n")
    
    # Verificar se já existe instalação
    if (destination / "template").exists() or (destination / ".cursor").exists():
        response = input(f"{Colors.YELLOW}⚠️  Já existe uma instalação. Deseja continuar? (s/N): {Colors.RESET}")
        if response.lower() not in ['s', 'sim', 'y', 'yes']:
            print(f"\n{Colors.BLUE}Operação cancelada.{Colors.RESET}")
            sys.exit(0)
    
    # Copiar templates
    if not copy_templates(destination):
        sys.exit(1)
    
    # Criar .cursor/rules
    if not create_cursor_rules(destination):
        sys.exit(1)
    
    # Mostrar próximos passos
    show_next_steps()
    
    sys.exit(0)


if __name__ == "__main__":
    main()

