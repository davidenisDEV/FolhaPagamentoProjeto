import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PayrollSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pagamento Fuzuê")
        self.file_path = "folha_pagamento.xlsx"
        
        # Valores das diárias
        self.daily_rates = {
            'gerente': 175,
            'subgerente': 160,
            'atendente': 120,
            'cozinha': 100,
            'bar': 200,
            'churrasqueiro': 150,
            'seguranca': 130
        }
        
        # Funcionários fixos
        self.fixed_employees = {
            'grace': 'atendente',
            'cleria': 'gerente',
            'lucas': 'subgerente',
            'emerson': 'atendente',
            'livia': 'atendente',
            'eli': 'atendente',
            'andressa': 'bar',
            'eddie': 'cozinha',
            'amiga eddie': 'cozinha',
            'anchieta': 'churrasqueiro'
        }
        
        # Configuração inicial
        self.columns = ['Data', 'Nome', 'Cargo', 'Dias', 'Adicional', 'Motivo', 'Adiantamento', 'Total Bruto', 'Total Líquido']
        self.load_or_create_data()
        self.create_interface()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_data(self):
        if os.path.exists(self.file_path):
            self.df = pd.read_excel(self.file_path)
        else:
            self.df = pd.DataFrame(columns=self.columns)

    def save_data(self):
        try:
            self.df.to_excel(self.file_path, index=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")

    def on_close(self):
        self.save_data()
        self.root.destroy()
    
    def load_or_create_data(self):
        if os.path.exists(self.file_path):
            self.df = pd.read_excel(self.file_path)
        else:
            self.df = pd.DataFrame(columns=self.columns)
            
    # Criar interface
    def create_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de Lançamentos
        self.create_main_tab()
        
        # Aba de Histórico
        self.create_history_tab()
        
        # Aba de Gestão de Funcionários
        self.create_employee_tab()
        
        # Aba de Relatórios Financeiros
        self.create_reports_tab()

    def create_main_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Lançamentos")
        
        # Campos de entrada
        fields = [
            ('Nome:', 'name_entry'),
            ('Cargo:', 'role_combobox', list(self.daily_rates.keys())),
            ('Dias Trabalhados:', 'days_entry'),
            ('Adicional:', 'additional_entry'),
            ('Motivo Adicional:', 'reason_entry'),
            ('Adiantamento:', 'advance_entry')
        ]
        
        for i, field in enumerate(fields):
            label = field[0]
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            if len(field) == 3:  # Combobox
                setattr(self, field[1], ttk.Combobox(frame, values=field[2], width=22))
            else:  # Entry
                setattr(self, field[1], ttk.Entry(frame, width=25))
            getattr(self, field[1]).grid(row=i, column=1, padx=5, pady=2)

        # Botões
        buttons = [
            ('Adicionar', self.add_entry),
            ('Editar', self.edit_entry),
            ('Deletar', self.delete_entry),
            ('Salvar Excel', self.save_to_excel)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(frame, text=text, command=command).grid(row=6, column=i, padx=5, pady=10)

        # Lista de registros
        self.listbox = tk.Listbox(frame, width=90, height=12)
        self.listbox.grid(row=7, column=0, columnspan=4, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.select_entry)
        
        # Totais
        self.total_label = ttk.Label(frame, text="Total Líquido: R$0.00 | Total Adiantamentos: R$0.00", font=('Arial', 10, 'bold'))
        self.total_label.grid(row=8, column=0, columnspan=4)

        self.update_display()

    def create_history_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Histórico")
        
        # Lista de datas
        ttk.Label(frame, text="Selecione a data:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.date_listbox = tk.Listbox(frame, width=20, height=10)
        self.date_listbox.grid(row=1, column=0, padx=5, pady=5)
        self.date_listbox.bind('<<ListboxSelect>>', self.show_history)

        # Detalhes do histórico
        self.history_text = tk.Text(frame, width=50, height=10, state='disabled')
        self.history_text.grid(row=1, column=1, padx=5, pady=5)

        # Atualizar lista de datas
        self.update_date_list()
    
    def create_employee_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Gestão de Funcionários")
        
        # Filtro por nome
        ttk.Label(frame, text="Nome do Funcionário:").grid(row=0, column=0, padx=5, pady=5)
        self.employee_name_entry = ttk.Entry(frame, width=30)
        self.employee_name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Buscar", command=self.show_employee_data).grid(row=0, column=2, padx=5, pady=5)
        
        # Histórico de pagamentos
        self.employee_history_text = tk.Text(frame, width=80, height=15, state='disabled')
        self.employee_history_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    def show_employee_data(self):
        name = self.employee_name_entry.get().strip().title()
        if not name:
            messagebox.showwarning("Aviso", "Digite o nome do funcionário.")
            return
        
        employee_data = self.df[self.df['Nome'] == name]
        if employee_data.empty:
            messagebox.showinfo("Info", f"Nenhum registro encontrado para {name}.")
            return
        
        self.employee_history_text.config(state='normal')
        self.employee_history_text.delete(1.0, tk.END)
        self.employee_history_text.insert(tk.END, f"Histórico de Pagamentos para {name}:\n\n")
        self.employee_history_text.insert(tk.END, employee_data.to_string(index=False))
        self.employee_history_text.config(state='disabled')

    def create_reports_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Relatórios Financeiros")
        
        # Filtros
        ttk.Label(frame, text="Período:").grid(row=0, column=0, padx=5, pady=5)
        self.report_period_combobox = ttk.Combobox(frame, values=["Semanal", "Mensal"], width=15)
        self.report_period_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.report_period_combobox.set("Mensal")
        ttk.Button(frame, text="Gerar Relatório", command=self.generate_report).grid(row=0, column=2, padx=5, pady=5)
        
        # Gráfico
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    def generate_report(self):
        period = self.report_period_combobox.get()
        if period == "Mensal":
            self.df['Data'] = pd.to_datetime(self.df['Data'], format='%d/%m/%Y')
            report_data = self.df.groupby(self.df['Data'].dt.to_period('M')).sum(numeric_only=True)
            report_data.index = report_data.index.strftime('%Y-%m')
        else:
            self.df['Data'] = pd.to_datetime(self.df['Data'], format='%d/%m/%Y')
            report_data = self.df.groupby(self.df['Data'].dt.to_period('W')).sum(numeric_only=True)
            report_data.index = report_data.index.strftime('%Y-%U')
        
        # Atualizar gráfico
        self.ax.clear()
        report_data['Total Bruto'].plot(kind='bar', ax=self.ax, color='skyblue')
        self.ax.set_title(f"Total de Pagamentos ({period})")
        self.ax.set_xlabel("Período")
        self.ax.set_ylabel("Valor (R$)")
        self.canvas.draw()

    def update_date_list(self):
        self.date_listbox.delete(0, tk.END)
        unique_dates = self.df['Data'].unique()
        for date in sorted(unique_dates):
            self.date_listbox.insert(tk.END, date)

    def show_history(self, event):
        selected = self.date_listbox.curselection()
        if selected:
            date = self.date_listbox.get(selected[0])
            history_df = self.df[self.df['Data'] == date]
            
            self.history_text.config(state='normal')
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(tk.END, f"Histórico para {date}:\n\n")
            self.history_text.insert(tk.END, history_df.to_string(index=False))
            self.history_text.config(state='disabled')

    def calculate_payment(self, role, days, additional, advance):
        bruto = (self.daily_rates[role] * days) + (additional * 1.1)
        liquido = bruto - advance
        return bruto, max(liquido, 0)

    def update_display(self):
        self.listbox.delete(0, tk.END)
        for _, row in self.df.iterrows():
            display_text = (f"{row['Data']} | {row['Nome']} | {row['Cargo']} | "
                            f"{row['Dias']} dias | R${row['Total Líquido']:.2f}")
            self.listbox.insert(tk.END, display_text)
        
        total_bruto = self.df['Total Bruto'].sum()
        total_adiantamento = self.df['Adiantamento'].sum()
        self.total_label.config(text=f"Total Bruto: R${total_bruto:.2f} | Total Líquido: R${total_bruto - total_adiantamento:.2f} | Adiantamentos: R${total_adiantamento:.2f}")

    def add_entry(self):
        try:
            name = self.name_entry.get().strip().lower()
            role = self.role_combobox.get().strip().lower()
            days = int(self.days_entry.get().strip())
            additional = float(self.additional_entry.get().strip())
            reason = self.reason_entry.get().strip()
            advance = float(self.advance_entry.get().strip())
            
            if not name or not role or not reason:
                raise ValueError("Preencha todos os campos obrigatórios.")
            
            if name in self.fixed_employees:
                role = self.fixed_employees[name]
            
            bruto, liquido = self.calculate_payment(role, days, additional, advance)
            current_date = datetime.now().strftime("%d/%m/%Y")
            
            new_entry = pd.DataFrame([{
                'Data': current_date,
                'Nome': name.title(),
                'Cargo': role,
                'Dias': days,
                'Adicional': additional,
                'Motivo': reason,
                'Adiantamento': advance,
                'Total Bruto': bruto,
                'Total Líquido': liquido
            }], columns=self.columns)
            
            self.df = pd.concat([self.df, new_entry], ignore_index=True)
            self.update_display()
            self.clear_entries()
            self.update_date_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar registro: {str(e)}")

    def edit_entry(self):
        selected = self.listbox.curselection()
        if selected:
            try:
                index = selected[0]
                name = self.name_entry.get().strip().lower()
                role = self.role_combobox.get().strip().lower()
                days = int(self.days_entry.get().strip())
                additional = float(self.additional_entry.get().strip())
                reason = self.reason_entry.get().strip()
                advance = float(self.advance_entry.get().strip())
                
                if name in self.fixed_employees:
                    role = self.fixed_employees[name]
                
                bruto, liquido = self.calculate_payment(role, days, additional, advance)
                
                self.df.at[index, 'Nome'] = name.title()
                self.df.at[index, 'Cargo'] = role
                self.df.at[index, 'Dias'] = days
                self.df.at[index, 'Adicional'] = additional
                self.df.at[index, 'Motivo'] = reason
                self.df.at[index, 'Adiantamento'] = advance
                self.df.at[index, 'Total Bruto'] = bruto
                self.df.at[index, 'Total Líquido'] = liquido
                
                self.update_display()
                self.clear_entries()
                self.update_date_list()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao editar registro: {str(e)}")

    def delete_entry(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.df = self.df.drop(index).reset_index(drop=True)
            self.update_display()
            self.clear_entries()
            self.update_date_list()

    def save_to_excel(self):
        try:
            self.df.to_excel(self.file_path, index=False)
            messagebox.showinfo("Sucesso", "Dados salvos no Excel com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.role_combobox.set('')
        self.days_entry.delete(0, tk.END)
        self.additional_entry.delete(0, tk.END)
        self.reason_entry.delete(0, tk.END)
        self.advance_entry.delete(0, tk.END)

    def select_entry(self, event):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            data = self.df.iloc[index]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, data['Nome'])
            self.role_combobox.set(data['Cargo'])
            self.days_entry.delete(0, tk.END)
            self.days_entry.insert(0, str(data['Dias']))
            self.additional_entry.delete(0, tk.END)
            self.additional_entry.insert(0, str(data['Adicional']))
            self.reason_entry.delete(0, tk.END)
            self.reason_entry.insert(0, data['Motivo'])
            self.advance_entry.delete(0, tk.END)
            self.advance_entry.insert(0, str(data['Adiantamento']))

if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollSystem(root)
    
    # Manual do Sistema
    manual = """=== MANUAL DO SISTEMA FUZUÊ ===

1. CADASTRO DE FUNCIONÁRIOS:
- Preencha todos os campos obrigatórios
- Funcionários fixos têm cargo automático
- Use valores decimais para adiantamentos

2. CÁLCULOS AUTOMÁTICOS:
- Valores calculados com base na diária do cargo
- Adicionais têm 10% de bonificação
- Adiantamentos são deduzidos do total

3. HISTÓRICO COMPLETO:
- Acesse todas as folhas por data
- Visualize detalhes completos
- Exporte para Excel a qualquer momento

4. EDIÇÃO SEGURA:
- Clique em um registro para editar
- Atualizações refletem imediatamente
- Histórico permanente e seguro

Dúvidas? Contate o desenvolvedor!"""
    
    messagebox.showinfo("Manual do Sistema", manual)
    root.mainloop()