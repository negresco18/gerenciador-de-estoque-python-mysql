#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- Sistema de Gerenciamento de Componentes
Sistema de gaveteiro para organização de componentes eletrônicos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pymysql
import json
import os
from datetime import datetime
from pathlib import Path

# =====================================================
# CONFIGURAÇÃO 
# =====================================================

def criar_config_gaveteiros_automatico():
    """Cria config_gaveteiros.json automaticamente se não existir"""
    config_file = "config_gaveteiros.json"
    
    if not Path(config_file).exists():
        print("Criando config_gaveteiros.json automaticamente...")
        
        config = {
            "gaveteiro_atual": 1,
            "gaveteiros": [
                {
                    "id": 1,
                    "nome": "Gaveteiro Principal",
                    "host": "127.0.0.1",
                    "user": "root",
                    "password": "",
                    "database": "gaveteiro"
                },
                {
                    "id": 2,
                    "nome": "Componentes Especiais",
                    "host": "127.0.0.1",
                    "user": "root",
                    "password": "",
                    "database": "gaveteiro_especiais"
                }
            ]
        }
        
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("config_gaveteiros.json criado automaticamente!")
            return True
        except Exception as e:
            print(f" Erro ao criar config_gaveteiros.json: {e}")
            return False
    
    return True

# Criar configuração automaticamente no início
criar_config_gaveteiros_automatico()

# =====================================================
# RESTANTE DO CÓDIGO ORIGINAL
# =====================================================

class GaveteiroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configuração do banco de dados
        self.conexao = None
        self.gaveteiro_atual = None
        self.carregar_configuracao_gaveteiro()
        self.conectar_banco()
        
        # Variáveis
        self.resultado_busca = []
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Criar interface
        self.criar_interface()
        
        # Iniciar relógio
        self.atualizar_relogio()
        
    def configurar_estilo(self):
        """Configura o estilo visual da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TButton', background='#4a90e2', foreground='#ffffff')
        style.configure('Treeview', background='#3c3c3c', foreground='#ffffff', fieldbackground='#3c3c3c')
        style.configure('Treeview.Heading', background='#4a90e2', foreground='#ffffff')
        
    def carregar_configuracao_gaveteiro(self):
        """Carrega a configuração do gaveteiro atual"""
        try:
            config_file = "config_gaveteiros.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                gaveteiro_id = config.get('gaveteiro_atual', 1)
                
                # Encontrar gaveteiro atual
                for gaveteiro in config['gaveteiros']:
                    if gaveteiro['id'] == gaveteiro_id:
                        self.gaveteiro_atual = gaveteiro
                        break
                
                if not self.gaveteiro_atual:
                    # Usar primeiro gaveteiro disponível
                    self.gaveteiro_atual = config['gaveteiros'][0]
            else:
                # Configuração padrão
                self.gaveteiro_atual = {
                    'id': 1,
                    'nome': 'Gaveteiro Principal',
                    'host': '127.0.0.1',
                    'user': 'root',
                    'password': '',
                    'database': 'gaveteiro'
                }
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configuração do gaveteiro:\n{e}")
            self.root.destroy()
    
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            self.conexao = pymysql.connect(
                host=self.gaveteiro_atual['host'],
                user=self.gaveteiro_atual['user'],
                password=self.gaveteiro_atual['password'],
                database=self.gaveteiro_atual['database'],
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{e}")
            self.root.destroy()
    
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal com gradiente
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cabeçalho
        self.criar_cabecalho(main_frame)
        
        # Frame de estatísticas
        self.criar_frame_estatisticas(main_frame)
        
        # Frame de operações
        self.criar_frame_operacoes(main_frame)
        
        # Frame de resultados
        self.criar_frame_resultados(main_frame)
        
        # Status bar
        self.criar_status_bar(main_frame)
    
    def criar_cabecalho(self, parent):
        """Cria o cabeçalho da aplicação"""
        header_frame = tk.Frame(parent, bg='#2b2b2b')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        
        # Relógio
        self.relogio_var = tk.StringVar()
        relogio = tk.Label(header_frame, 
                          textvariable=self.relogio_var,
                          font=('Arial', 12),
                          bg='#2b2b2b', fg='#ffffff')
        relogio.pack(side=tk.RIGHT)
        
        # Subtítulo
        subtitulo = tk.Label(header_frame,
                            text="Sistema de Gerenciamento de Componentes",
                            font=('Arial', 12),
                            bg='#2b2b2b', fg='#cccccc')
        subtitulo.pack(side=tk.LEFT, padx=(20, 0))
        
        # Frame para botões de troca
        troca_frame = tk.Frame(header_frame, bg='#2b2b2b')
        troca_frame.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Gaveteiro atual
        self.gaveteiro_label = tk.Label(troca_frame,
                                       text=f" {self.gaveteiro_atual['nome']}",
                                       font=('Arial', 10, 'bold'),
                                       bg='#2b2b2b', fg='#27ae60')
        self.gaveteiro_label.pack(side=tk.TOP, pady=(0, 5))
        
        # Botões de troca
        botoes_troca_frame = tk.Frame(troca_frame, bg='#2b2b2b')
        botoes_troca_frame.pack(side=tk.TOP)
        
        # Botão Gaveteiro
        btn_gaveteiro = tk.Button(botoes_troca_frame,
                                 text=" Gaveteiro",
                                 command=lambda: self.trocar_para_gaveteiro(1),
                                 font=('Arial', 9, 'bold'),
                                 bg='#4a90e2' if self.gaveteiro_atual['id'] == 1 else '#666666',
                                 fg='#ffffff',
                                 relief=tk.FLAT, padx=10, pady=3)
        btn_gaveteiro.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão Componentes Especiais
        btn_especiais = tk.Button(botoes_troca_frame,
                                 text="⭐ Especiais",
                                 command=lambda: self.trocar_para_gaveteiro(2),
                                 font=('Arial', 9, 'bold'),
                                 bg='#f39c12' if self.gaveteiro_atual['id'] == 2 else '#666666',
                                 fg='#ffffff',
                                 relief=tk.FLAT, padx=10, pady=3)
        btn_especiais.pack(side=tk.LEFT)
        
        # Armazenar referências dos botões
        self.btn_gaveteiro = btn_gaveteiro
        self.btn_especiais = btn_especiais
    

    
    def criar_frame_estatisticas(self, parent):
        """Cria o frame de estatísticas"""
        stats_frame = tk.Frame(parent, bg='#2b2b2b')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Cards de estatísticas
        self.criar_card_estatistica(stats_frame, " Total de Componentes", "0", 0)
        self.criar_card_estatistica(stats_frame, " Gavetas Utilizadas", "0", 1)
        self.criar_card_estatistica(stats_frame, " Gavetas Vazias", "0", 2)
        self.criar_card_estatistica(stats_frame, " Última Atualização", "Agora", 3)
        
        # Atualizar estatísticas
        self.atualizar_estatisticas()
    
    def criar_card_estatistica(self, parent, titulo, valor, coluna):
        """Cria um card de estatística"""
        card = tk.Frame(parent, bg='#3c3c3c', relief=tk.RAISED, bd=1)
        card.grid(row=0, column=coluna, padx=5, pady=5, sticky='ew')
        parent.columnconfigure(coluna, weight=1)
        
        # Título
        tk.Label(card, text=titulo,
                font=('Arial', 10),
                bg='#3c3c3c', fg='#cccccc').pack(pady=(10, 5))
        
        # Valor
        valor_var = tk.StringVar(value=valor)
        tk.Label(card, textvariable=valor_var,
                font=('Arial', 16, 'bold'),
                bg='#3c3c3c', fg='#4a90e2').pack(pady=(0, 10))
        
        # Armazenar referência
        if not hasattr(self, 'stats_vars'):
            self.stats_vars = {}
        self.stats_vars[titulo] = valor_var
    
    def criar_frame_operacoes(self, parent):
        """Cria o frame de operações"""
        opcoes_frame = tk.LabelFrame(parent,
                                    text=" Operações",
                                    font=('Arial', 12, 'bold'),
                                    bg='#2b2b2b', fg='#ffffff',
                                    relief=tk.RAISED, bd=2)
        opcoes_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Conteúdo do frame
        content_frame = tk.Frame(opcoes_frame, bg='#2b2b2b')
        content_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Botões das operações
        botoes = [
            (" Buscar Componente", self.buscar_componente),
            (" Buscar por Gaveta", self.buscar_por_gaveta),
            (" Adicionar Componente", self.adicionar_componente),
            (" Editar Componente", self.editar_componente),
            (" Excluir Componente", self.excluir_componente),
            (" Ver Logs", self.ver_logs),
            (" Atualizar", self.atualizar_interface_automaticamente)
        ]
        
        for i, (texto, comando) in enumerate(botoes):
            btn = tk.Button(content_frame,
                           text=texto,
                           command=comando,
                           font=('Arial', 11),
                           bg='#4a90e2', fg='#ffffff',
                           relief=tk.FLAT,
                           padx=20, pady=10,
                           cursor='hand2')
            btn.grid(row=0, column=i, padx=5, pady=5)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#5ba0f2'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#4a90e2'))
    
    def criar_frame_resultados(self, parent):
        """Cria o frame de resultados"""
        resultados_frame = tk.LabelFrame(parent,
                                        text="📋 Resultados",
                                        font=('Arial', 12, 'bold'),
                                        bg='#2b2b2b', fg='#ffffff',
                                        relief=tk.RAISED, bd=2)
        resultados_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Frame interno
        inner_frame = tk.Frame(resultados_frame, bg='#2b2b2b')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview para resultados
        colunas = ('ID', 'Nome', 'Tipo', 'Gaveta', 'Espaço', 'Data Criação')
        self.tree = ttk.Treeview(inner_frame, columns=colunas, show='headings', height=15)
        
        # Configurar colunas
        for col in colunas:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=80)
            elif col == 'Espaço':
                self.tree.column(col, width=80)
            elif col == 'Gaveta':
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=180)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def criar_status_bar(self, parent):
        """Cria a barra de status"""
        self.status_var = tk.StringVar()
        self.status_var.set("Sistema pronto. Use as operações acima para gerenciar os componentes.")
        
        status_bar = tk.Label(parent,
                             textvariable=self.status_var,
                             font=('Arial', 10),
                             bg='#3c3c3c', fg='#ffffff',
                             relief=tk.SUNKEN, bd=1)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def atualizar_relogio(self):
        """Atualiza o relógio"""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.relogio_var.set(agora)
        self.root.after(1000, self.atualizar_relogio)
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas"""
        try:
            with self.conexao.cursor() as cursor:
                # Total de componentes
                cursor.execute("SELECT COUNT(*) as total FROM componentes")
                total = cursor.fetchone()['total']
                self.stats_vars[" Total de Componentes"].set(str(total))
                
                # Gavetas utilizadas
                cursor.execute("SELECT COUNT(DISTINCT gaveta_id) as gavetas FROM componentes WHERE gaveta_id IS NOT NULL")
                gavetas_utilizadas = cursor.fetchone()['gavetas']
                self.stats_vars[" Gavetas Utilizadas"].set(str(gavetas_utilizadas))
                
                # Total de gavetas disponíveis (detecta automaticamente)
                total_gavetas = self.obter_total_gavetas()
                
                # Gavetas vazias
                gavetas_vazias = total_gavetas - gavetas_utilizadas
                self.stats_vars[" Gavetas Vazias"].set(str(gavetas_vazias))
                
                # Última atualização
                agora = datetime.now().strftime("%H:%M:%S")
                self.stats_vars[" Última Atualização"].set(agora)
                
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def registrar_log(self, acao, detalhes=""):
        """Registra uma ação no log"""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO logs (tecnico, acao, detalhes) 
                    VALUES (%s, %s, %s)
                """, ("Sistema", acao, detalhes))
                self.conexao.commit()
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
    

    
    def buscar_componente(self):
        """Busca componente por nome"""
            
        nome = simpledialog.askstring("Buscar Componente", 
                                    "Digite o nome (ou parte do nome) do componente:")
        if not nome:
            return
            
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM componentes WHERE nome LIKE %s ORDER BY nome", 
                             (f"%{nome}%",))
                resultado = cursor.fetchall()
            
            self.limpar_resultados()
            
            if resultado:
                for item in resultado:
                    self.tree.insert('', 'end', values=(
                        item['id'],
                        item['nome'],
                        item.get('tipo', 'N/A'),
                        item.get('gaveta_id', 'N/A'),
                        item.get('espaco_id', 'N/A'),
                        item.get('created_at', 'N/A')
                    ))
                self.status_var.set(f"Encontrados {len(resultado)} componente(s) com o nome '{nome}'")
                self.registrar_log("BUSCAR_COMPONENTE", f"Busca por: {nome} - {len(resultado)} resultados")
            else:
                self.status_var.set(f"Nenhum componente encontrado com o nome '{nome}'")
                self.registrar_log("BUSCAR_COMPONENTE", f"Busca por: {nome} - 0 resultados")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar componente: {e}")
            self.registrar_log("ERRO", f"Erro na busca: {e}")
    
    def buscar_por_gaveta(self):
        """Busca componentes por gaveta"""
        
        # Detectar o número máximo de gavetas disponíveis
        total_gavetas = self.obter_total_gavetas()
            
        gaveta_id = simpledialog.askstring("Buscar por Gaveta", 
                                         f"Digite o ID da gaveta (1-{total_gavetas}):")
        if not gaveta_id:
            return
            
        try:
            gaveta_id = int(gaveta_id)
            if not (1 <= gaveta_id <= total_gavetas):
                messagebox.showwarning("Aviso", f"Gaveta deve estar entre 1 e {total_gavetas}!")
                return
        except ValueError:
            messagebox.showwarning("Aviso", "ID da gaveta deve ser um número!")
            return
            
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nome, tipo, gaveta_id, espaco_id, created_at 
                    FROM componentes 
                    WHERE gaveta_id = %s 
                    ORDER BY espaco_id, nome
                """, (gaveta_id,))
                resultado = cursor.fetchall()
            
            self.limpar_resultados()
            
            if resultado:
                for item in resultado:
                    self.tree.insert('', 'end', values=(
                        item['id'],
                        item['nome'],
                        item.get('tipo', 'N/A'),
                        item['gaveta_id'],
                        item.get('espaco_id', 'N/A'),
                        item.get('created_at', 'N/A')
                    ))
                self.status_var.set(f"Gaveta {gaveta_id}: {len(resultado)} componente(s) encontrado(s)")
                self.registrar_log("BUSCAR_GAVETA", f"Gaveta {gaveta_id} - {len(resultado)} componentes")
            else:
                self.status_var.set(f"Gaveta {gaveta_id}: Nenhum componente encontrado")
                self.registrar_log("BUSCAR_GAVETA", f"Gaveta {gaveta_id} - vazia")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar por gaveta: {e}")
            self.registrar_log("ERRO", f"Erro na busca por gaveta: {e}")
    
    def adicionar_componente(self):
        """Adiciona um novo componente"""
            
        # Janela de adicionar componente
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Adicionar Componente")
        dialog.geometry("600x500")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar janela
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Frame principal
        frame = tk.Frame(dialog, bg='#2b2b2b')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(frame, text="➕ Adicionar Novo Componente",
                font=('Arial', 16, 'bold'),
                bg='#2b2b2b', fg='#4a90e2').pack(pady=(0, 20))
        
        # Campos
        campos_frame = tk.Frame(frame, bg='#2b2b2b')
        campos_frame.pack(fill=tk.X, pady=10)
        
        # Nome
        tk.Label(campos_frame, text="Nome do Componente:",
                font=('Arial', 11),
                bg='#2b2b2b', fg='#ffffff').pack(anchor=tk.W)
        nome_var = tk.StringVar()
        nome_entry = tk.Entry(campos_frame, textvariable=nome_var,
                             font=('Arial', 11), width=40,
                             bg='#3c3c3c', fg='#ffffff',
                             insertbackground='#ffffff')
        nome_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Tipo
        tk.Label(campos_frame, text="Tipo (opcional):",
                font=('Arial', 11),
                bg='#2b2b2b', fg='#ffffff').pack(anchor=tk.W)
        tipo_var = tk.StringVar()
        tipo_entry = tk.Entry(campos_frame, textvariable=tipo_var,
                             font=('Arial', 11), width=40,
                             bg='#3c3c3c', fg='#ffffff',
                             insertbackground='#ffffff')
        tipo_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Gaveta (será atualizado dinamicamente)
        self.gaveta_label = tk.Label(campos_frame, text="Gaveta ID (1-449):",
                font=('Arial', 11),
                bg='#2b2b2b', fg='#ffffff')
        self.gaveta_label.pack(anchor=tk.W)
        
        # Atualizar o label com o número correto de gavetas
        self.atualizar_label_gaveta()
        gaveta_var = tk.StringVar()
        gaveta_entry = tk.Entry(campos_frame, textvariable=gaveta_var,
                               font=('Arial', 11), width=40,
                               bg='#3c3c3c', fg='#ffffff',
                               insertbackground='#ffffff')
        gaveta_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Espaço na gaveta
        tk.Label(campos_frame, text="Espaço na Gaveta (1-6):",
                font=('Arial', 11),
                bg='#2b2b2b', fg='#ffffff').pack(anchor=tk.W)
        espaco_var = tk.StringVar()
        espaco_entry = tk.Entry(campos_frame, textvariable=espaco_var,
                               font=('Arial', 11), width=40,
                               bg='#3c3c3c', fg='#ffffff',
                               insertbackground='#ffffff')
        espaco_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Botões
        botoes_frame = tk.Frame(frame, bg='#2b2b2b')
        botoes_frame.pack(fill=tk.X, pady=20)
        
        def salvar():
            nome = nome_var.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Nome do componente é obrigatório!")
                return
                
            tipo = tipo_var.get().strip() or None
            gaveta_input = gaveta_var.get().strip()
            espaco_input = espaco_var.get().strip()
            
            gaveta_id = None
            espaco_id = None
            
            if gaveta_input:
                try:
                    gaveta_id = int(gaveta_input)
                    # Detectar o número máximo de gavetas disponíveis
                    total_gavetas = self.obter_total_gavetas()
                    
                    if not (1 <= gaveta_id <= total_gavetas):
                        messagebox.showwarning("Aviso", f"Gaveta deve estar entre 1 e {total_gavetas}!")
                        return
                except ValueError:
                    messagebox.showwarning("Aviso", "ID da gaveta deve ser um número!")
                    return
            
            if espaco_input:
                try:
                    espaco_id = int(espaco_input)
                    if not (1 <= espaco_id <= 6):
                        messagebox.showwarning("Aviso", "Espaço deve estar entre 1 e 6!")
                        return
                except ValueError:
                    messagebox.showwarning("Aviso", "Espaço deve ser um número!")
                    return
            
            # Verificar se o espaço já está ocupado
            if gaveta_id and espaco_id:
                try:
                    with self.conexao.cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) as total FROM componentes 
                            WHERE gaveta_id = %s AND espaco_id = %s
                        """, (gaveta_id, espaco_id))
                        if cursor.fetchone()['total'] > 0:
                            messagebox.showwarning("Aviso", f"Espaço {espaco_id} da gaveta {gaveta_id} já está ocupado!")
                            return
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao verificar espaço: {e}")
                    return
            
            try:
                with self.conexao.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO componentes (nome, tipo, gaveta_id, espaco_id) 
                        VALUES (%s, %s, %s, %s)
                    """, (nome, tipo, gaveta_id, espaco_id))
                    self.conexao.commit()
                    
                    id_criado = cursor.lastrowid
                    messagebox.showinfo("Sucesso", 
                                      f"Componente adicionado com sucesso!\n\n"
                                      f"ID: {id_criado}\n"
                                      f"Nome: {nome}\n"
                                      f"Tipo: {tipo or 'N/A'}\n"
                                      f"Gaveta: {gaveta_id or 'N/A'}\n"
                                      f"Espaço: {espaco_id or 'N/A'}")
                    
                    self.registrar_log("ADICIONAR_COMPONENTE", 
                                     f"ID: {id_criado}, Nome: {nome}, Gaveta: {gaveta_id}, Espaço: {espaco_id}")
                    self.atualizar_estatisticas()
                    self.atualizar_interface_automaticamente()
                    dialog.destroy()
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar componente: {e}")
                self.registrar_log("ERRO", f"Erro ao adicionar: {e}")
        
        tk.Button(botoes_frame, text="💾 Salvar",
                 command=salvar,
                 font=('Arial', 11),
                 bg='#4a90e2', fg='#ffffff',
                 relief=tk.FLAT, padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(botoes_frame, text="❌ Cancelar",
                 command=dialog.destroy,
                 font=('Arial', 11),
                 bg='#e74c3c', fg='#ffffff',
                 relief=tk.FLAT, padx=20, pady=10).pack(side=tk.LEFT)
        
        nome_entry.focus()
    
    def obter_total_gavetas(self):
        """Obtém o total de gavetas disponíveis"""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("SELECT MAX(gaveta_id) as max_gaveta FROM componentes WHERE gaveta_id IS NOT NULL")
                max_gaveta_result = cursor.fetchone()
                max_gaveta = max_gaveta_result['max_gaveta'] if max_gaveta_result['max_gaveta'] else 0
                
                # Se for o gaveteiro de componentes especiais (ID 2), usar apenas o máximo real
                if self.gaveteiro_atual and self.gaveteiro_atual['id'] == 2:
                    return max_gaveta  # Apenas as gavetas realmente utilizadas
                else:
                    return max(449, max_gaveta)  # Mínimo 449 para o gaveteiro principal
                    
        except Exception as e:
            print(f"Erro ao obter total de gavetas: {e}")
            # Valor padrão baseado no tipo de gaveteiro
            if self.gaveteiro_atual and self.gaveteiro_atual['id'] == 2:
                return 11  # Padrão para componentes especiais
            else:
                return 449  # Padrão para gaveteiro principal
    
    def atualizar_label_gaveta(self):
        """Atualiza o label da gaveta com o número correto"""
        try:
            total_gavetas = self.obter_total_gavetas()
            if hasattr(self, 'gaveta_label'):
                self.gaveta_label.config(text=f"Gaveta ID (1-{total_gavetas}):")
        except Exception as e:
            print(f"Erro ao atualizar label da gaveta: {e}")
    
    def editar_componente(self):
        """Edita um componente existente"""
            
        id_componente = simpledialog.askstring("Editar Componente", 
                                             "Digite o ID do componente que deseja editar:")
        if not id_componente:
            return
            
        try:
            id_componente = int(id_componente)
        except ValueError:
            messagebox.showwarning("Aviso", "ID do componente deve ser um número!")
            return
            
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM componentes WHERE id = %s", (id_componente,))
                componente = cursor.fetchone()
                
                if not componente:
                    messagebox.showwarning("Aviso", f"Componente com ID {id_componente} não encontrado!")
                    return
                
                # Janela de edição
                dialog = tk.Toplevel(self.root)
                dialog.title("✏️ Editar Componente")
                dialog.geometry("600x500")
                dialog.configure(bg='#2b2b2b')
                dialog.transient(self.root)
                dialog.grab_set()
                
                # Frame principal
                frame = tk.Frame(dialog, bg='#2b2b2b')
                frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                # Título
                tk.Label(frame, text=f" Editar Componente - ID: {id_componente}",
                        font=('Arial', 16, 'bold'),
                        bg='#2b2b2b', fg='#4a90e2').pack(pady=(0, 20))
                
                # Campos
                campos_frame = tk.Frame(frame, bg='#2b2b2b')
                campos_frame.pack(fill=tk.X, pady=10)
                
                # Nome
                tk.Label(campos_frame, text="Nome do Componente:",
                        font=('Arial', 11),
                        bg='#2b2b2b', fg='#ffffff').pack(anchor=tk.W)
                nome_var = tk.StringVar(value=componente['nome'])
                nome_entry = tk.Entry(campos_frame, textvariable=nome_var,
                                     font=('Arial', 11), width=40,
                                     bg='#3c3c3c', fg='#ffffff',
                                     insertbackground='#ffffff')
                nome_entry.pack(fill=tk.X, pady=(5, 15))
                
                # Tipo
                tk.Label(campos_frame, text="Tipo:",
                        font=('Arial', 11),
                        bg='#2b2b2b', fg='#ffffff').pack(anchor=tk.W)
                tipo_var = tk.StringVar(value=componente.get('tipo', ''))
                tipo_entry = tk.Entry(campos_frame, textvariable=tipo_var,
                                     font=('Arial', 11), width=40,
                                     bg='#3c3c3c', fg='#ffffff',
                                     insertbackground='#ffffff')
                tipo_entry.pack(fill=tk.X, pady=(5, 15))
                
                # Gaveta (será atualizado dinamicamente)
                gaveta_label = tk.Label(campos_frame, text="Gaveta ID (1-449):",
                        font=('Arial', 11),
                        bg='#2b2b2b', fg='#ffffff')
                gaveta_label.pack(anchor=tk.W)
                
                # Atualizar o label com o número correto de gavetas
                try:
                    total_gavetas = self.obter_total_gavetas()
                    gaveta_label.config(text=f"Gaveta ID (1-{total_gavetas}):")
                except Exception as e:
                    print(f"Erro ao atualizar label da gaveta: {e}")
                gaveta_var = tk.StringVar(value=str(componente.get('gaveta_id', '')))
                gaveta_entry = tk.Entry(campos_frame, textvariable=gaveta_var,
                                       font=('Arial', 11), width=40,
                                       bg='#3c3c3c', fg='#ffffff',
                                       insertbackground='#ffffff')
                gaveta_entry.pack(fill=tk.X, pady=(5, 15))
                
                # Espaço na gaveta
                tk.Label(campos_frame, text="Espaço na Gaveta (1-6):",
                        font=('Arial', 11),
                        bg='#2b2b2b', fg='#ffffff').pack(anchor=tk.W)
                espaco_var = tk.StringVar(value=str(componente.get('espaco_id', '')))
                espaco_entry = tk.Entry(campos_frame, textvariable=espaco_var,
                                       font=('Arial', 11), width=40,
                                       bg='#3c3c3c', fg='#ffffff',
                                       insertbackground='#ffffff')
                espaco_entry.pack(fill=tk.X, pady=(5, 20))
                
                # Botões
                botoes_frame = tk.Frame(frame, bg='#2b2b2b')
                botoes_frame.pack(fill=tk.X, pady=20)
                
                def salvar_edicao():
                    nome = nome_var.get().strip()
                    if not nome:
                        messagebox.showwarning("Aviso", "Nome do componente é obrigatório!")
                        return
                        
                    tipo = tipo_var.get().strip() or None
                    gaveta_input = gaveta_var.get().strip()
                    espaco_input = espaco_var.get().strip()
                    
                    gaveta_id = None
                    espaco_id = None
                    
                    if gaveta_input:
                        try:
                            gaveta_id = int(gaveta_input)
                            # Detectar o número máximo de gavetas disponíveis
                            total_gavetas = self.obter_total_gavetas()
                            
                            if not (1 <= gaveta_id <= total_gavetas):
                                messagebox.showwarning("Aviso", f"Gaveta deve estar entre 1 e {total_gavetas}!")
                                return
                        except ValueError:
                            messagebox.showwarning("Aviso", "ID da gaveta deve ser um número!")
                            return
                    
                    if espaco_input:
                        try:
                            espaco_id = int(espaco_input)
                            if not (1 <= espaco_id <= 6):
                                messagebox.showwarning("Aviso", "Espaço deve estar entre 1 e 6!")
                                return
                        except ValueError:
                            messagebox.showwarning("Aviso", "Espaço deve ser um número!")
                            return
                    
                    # Verificar se o espaço já está ocupado (exceto pelo próprio componente)
                    if gaveta_id and espaco_id:
                        try:
                            with self.conexao.cursor() as cursor:
                                cursor.execute("""
                                    SELECT COUNT(*) as total FROM componentes 
                                    WHERE gaveta_id = %s AND espaco_id = %s AND id != %s
                                """, (gaveta_id, espaco_id, id_componente))
                                if cursor.fetchone()['total'] > 0:
                                    messagebox.showwarning("Aviso", f"Espaço {espaco_id} da gaveta {gaveta_id} já está ocupado!")
                                    return
                        except Exception as e:
                            messagebox.showerror("Erro", f"Erro ao verificar espaço: {e}")
                            return
                    
                    try:
                        with self.conexao.cursor() as cursor:
                            cursor.execute("""
                                UPDATE componentes 
                                SET nome = %s, tipo = %s, gaveta_id = %s, espaco_id = %s
                                WHERE id = %s
                            """, (nome, tipo, gaveta_id, espaco_id, id_componente))
                            self.conexao.commit()
                            
                            messagebox.showinfo("Sucesso", 
                                              f"Componente atualizado com sucesso!\n\n"
                                              f"ID: {id_componente}\n"
                                              f"Nome: {nome}\n"
                                              f"Tipo: {tipo or 'N/A'}\n"
                                              f"Gaveta: {gaveta_id or 'N/A'}\n"
                                              f"Espaço: {espaco_id or 'N/A'}")
                            
                            self.registrar_log("EDITAR_COMPONENTE", 
                                             f"ID: {id_componente}, Nome: {nome}, Gaveta: {gaveta_id}, Espaço: {espaco_id}")
                            self.atualizar_estatisticas()
                            self.atualizar_interface_automaticamente()
                            dialog.destroy()
                            
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao atualizar componente: {e}")
                        self.registrar_log("ERRO", f"Erro ao editar: {e}")
                
                tk.Button(botoes_frame, text="💾 Salvar",
                         command=salvar_edicao,
                         font=('Arial', 11),
                         bg='#4a90e2', fg='#ffffff',
                         relief=tk.FLAT, padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
                
                tk.Button(botoes_frame, text=" Cancelar",
                         command=dialog.destroy,
                         font=('Arial', 11),
                         bg='#e74c3c', fg='#ffffff',
                         relief=tk.FLAT, padx=20, pady=10).pack(side=tk.LEFT)
                
                nome_entry.focus()
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar componente: {e}")
            self.registrar_log("ERRO", f"Erro ao editar: {e}")
    
    def excluir_componente(self):
        """Exclui um componente"""
            
        id_componente = simpledialog.askstring("Excluir Componente", 
                                             "Digite o ID do componente que deseja excluir:")
        if not id_componente:
            return
            
        try:
            id_componente = int(id_componente)
        except ValueError:
            messagebox.showwarning("Aviso", "ID do componente deve ser um número!")
            return
            
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM componentes WHERE id = %s", (id_componente,))
                componente = cursor.fetchone()
                
                if componente:
                    resposta = messagebox.askyesno("Confirmar Exclusão", 
                                                 f"Tem certeza que deseja excluir este componente?\n\n"
                                                 f"ID: {componente['id']}\n"
                                                 f"Nome: {componente['nome']}\n"
                                                 f"Tipo: {componente.get('tipo', 'N/A')}\n"
                                                 f"Gaveta: {componente.get('gaveta_id', 'N/A')}")
                    
                    if resposta:
                        cursor.execute("DELETE FROM componentes WHERE id = %s", (id_componente,))
                        self.conexao.commit()
                        messagebox.showinfo("Sucesso", "Componente excluído com sucesso!")
                        self.status_var.set(f"Componente ID {id_componente} excluído")
                        self.registrar_log("EXCLUIR_COMPONENTE", 
                                         f"ID: {id_componente}, Nome: {componente['nome']}")
                        self.atualizar_estatisticas()
                        self.atualizar_interface_automaticamente()
                else:
                    messagebox.showwarning("Aviso", f"Componente com ID {id_componente} não encontrado!")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir componente: {e}")
            self.registrar_log("ERRO", f"Erro ao excluir: {e}")
    
    def ver_logs(self):
        """Mostra os logs do sistema"""
            
        # Janela de logs
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Logs do Sistema")
        dialog.geometry("800x600")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        frame = tk.Frame(dialog, bg='#2b2b2b')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(frame, text="📋 Logs de Auditoria",
                font=('Arial', 16, 'bold'),
                bg='#2b2b2b', fg='#4a90e2').pack(pady=(0, 20))
        
        # Treeview para logs
        colunas = ('ID', 'Técnico', 'Ação', 'Detalhes', 'Data/Hora')
        tree = ttk.Treeview(frame, columns=colunas, show='headings', height=20)
        
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Carregar logs
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM logs 
                    ORDER BY data_hora DESC 
                    LIMIT 100
                """)
                logs = cursor.fetchall()
                
                for log in logs:
                    tree.insert('', 'end', values=(
                        log['id'],
                        log['tecnico'],
                        log['acao'],
                        log.get('detalhes', ''),
                        log['data_hora']
                    ))
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar logs: {e}")
    
    def limpar_resultados(self):
        """Limpa os resultados da tabela"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def atualizar_interface_automaticamente(self):
        """Atualiza automaticamente a interface após mudanças no banco"""
        try:
            # Atualizar estatísticas
            self.atualizar_estatisticas()
            
            # Atualizar labels de gaveta
            self.atualizar_label_gaveta()
            
            # Se há resultados na tabela, recarregar
            if self.tree.get_children():
                # Salvar o último filtro aplicado (se houver)
                # Por enquanto, apenas limpar e mostrar todos
                self.limpar_resultados()
                
                # Recarregar todos os componentes
                with self.conexao.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, nome, tipo, gaveta_id, espaco_id, created_at 
                        FROM componentes 
                        ORDER BY gaveta_id, espaco_id, nome
                    """)
                    resultado = cursor.fetchall()
                    
                    for item in resultado:
                        self.tree.insert('', 'end', values=(
                            item['id'],
                            item['nome'],
                            item.get('tipo', 'N/A'),
                            item.get('gaveta_id', 'N/A'),
                            item.get('espaco_id', 'N/A'),
                            item.get('created_at', 'N/A')
                        ))
                
                self.status_var.set(f"Interface atualizada - {len(resultado)} componente(s) carregado(s)")
                
        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")
    
    def adicionar_botao_atualizar(self):
        """Adiciona botão de atualização manual"""
        # Adicionar botão de atualização na barra de operações
        btn_atualizar = tk.Button(self.root,
                                 text="🔄 Atualizar",
                                 command=self.atualizar_interface_automaticamente,
                                 font=('Arial', 11),
                                 bg='#27ae60', fg='#ffffff',
                                 relief=tk.FLAT,
                                 padx=20, pady=10,
                                 cursor='hand2')
        btn_atualizar.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)
    
    def on_closing(self):
        """Função chamada ao fechar a aplicação"""
        if self.conexao:
            self.conexao.close()
        self.root.destroy()

    def trocar_para_gaveteiro(self, gaveteiro_id):
        """Troca para um gaveteiro específico"""
        try:
            # Verificar se já está no gaveteiro selecionado
            if self.gaveteiro_atual['id'] == gaveteiro_id:
                return
            
            # Carregar configuração
            config_file = "config_gaveteiros.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Encontrar o gaveteiro
            novo_gaveteiro = None
            for gaveteiro in config['gaveteiros']:
                if gaveteiro['id'] == gaveteiro_id:
                    novo_gaveteiro = gaveteiro
                    break
            
            if not novo_gaveteiro:
                messagebox.showerror("Erro", "Gaveteiro não encontrado!")
                return
            
            # Testar conexão antes de trocar
            try:
                conexao_teste = pymysql.connect(
                    host=novo_gaveteiro['host'],
                    user=novo_gaveteiro['user'],
                    password=novo_gaveteiro['password'],
                    database=novo_gaveteiro['database'],
                    cursorclass=pymysql.cursors.DictCursor
                )
                conexao_teste.close()
            except Exception as e:
                messagebox.showerror("Erro de Conexão", 
                                   f"Não foi possível conectar ao gaveteiro '{novo_gaveteiro['nome']}':\n{e}\n\n"
                                   f"Verifique se o database '{novo_gaveteiro['database']}' existe.")
                return
            
            # Confirmar troca
            if messagebox.askyesno("Confirmar Troca", 
                                 f"Trocar para '{novo_gaveteiro['nome']}'?\n\n"
                                 f"Database: {novo_gaveteiro['database']}"):
                
                # Salvar nova configuração
                config['gaveteiro_atual'] = gaveteiro_id
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                # Atualizar gaveteiro atual
                self.gaveteiro_atual = novo_gaveteiro
                
                # Fechar conexão anterior
                if self.conexao:
                    self.conexao.close()
                
                # Conectar ao novo banco
                self.conectar_banco()
                
                # Atualizar interface de forma mais segura
                try:
                    self.reinicializar_interface()
                except Exception as e:
                    print(f"Erro na reinicialização: {e}")
                    # Fallback simples
                    self.status_var.set(f"Trocado para {novo_gaveteiro['nome']}")
                    if hasattr(self, 'gaveteiro_label'):
                        self.gaveteiro_label.configure(text=f" {novo_gaveteiro['nome']}")
                
                # Mostrar mensagem de sucesso
                messagebox.showinfo("Sucesso", 
                                  f"Trocado para '{novo_gaveteiro['nome']}' com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao trocar gaveteiro:\n{e}")
    
    def reinicializar_interface(self):
        """Reinicializa a interface após troca de gaveteiro"""
        try:
            # Limpar resultados
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Atualizar estatísticas
            self.atualizar_estatisticas()
            
            # Atualizar label do gaveteiro atual
            if hasattr(self, 'gaveteiro_label'):
                self.gaveteiro_label.configure(text=f" {self.gaveteiro_atual['nome']}")
            
            # Atualizar botões de troca
            self.atualizar_botoes_troca()
            
            # Atualizar status
            self.status_var.set(f"Trocado para {self.gaveteiro_atual['nome']}. Sistema pronto.")
            
            # Forçar atualização da interface de forma mais segura
            try:
                self.root.after(100, self.root.update_idletasks)
                self.root.after(200, self.root.update)
            except:
                pass
            
        except Exception as e:
            print(f"Erro ao reinicializar interface: {e}")
            # Em caso de erro, tentar uma atualização mais simples
            try:
                self.status_var.set(f"Trocado para {self.gaveteiro_atual['nome']}")
                if hasattr(self, 'gaveteiro_label'):
                    self.gaveteiro_label.configure(text=f"📦 {self.gaveteiro_atual['nome']}")
            except:
                pass
    
    def atualizar_botoes_troca(self):
        """Atualiza a aparência dos botões de troca de gaveteiro"""
        try:
            if hasattr(self, 'btn_gaveteiro') and hasattr(self, 'btn_especiais'):
                # Atualizar cor do botão Gaveteiro Principal
                if self.gaveteiro_atual['id'] == 1:
                    self.btn_gaveteiro.configure(bg='#4a90e2')
                    self.btn_especiais.configure(bg='#666666')
                else:
                    self.btn_gaveteiro.configure(bg='#666666')
                    self.btn_especiais.configure(bg='#f39c12')
        except Exception as e:
            print(f"Erro ao atualizar botões de troca: {e}")

def main():
    root = tk.Tk()
    app = GaveteiroApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()