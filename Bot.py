#Bibliotecas
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import asyncio  #esse aqui é pra não quebrar nada

#IDs de configuração
IdDoServidor = ID  #ID do servidor
IdDoCargo = ID  #aqui vai o cargo que vai ser setado
IdDoCanalConfirmarRec = ID  #confirmação de recrutamento
IdDoCanalLogs = ID  #logs do Recrutamento
IdDoCanalLogsAguia = ID  #aqui é o logs aguia

#Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

#----------------- Views -----------------#


#aqui é o botão de confirmação do log
class ConfirmacaoView(View):

    def __init__(self, usuario: discord.Member):
        super().__init__(timeout=None)
        self.usuario = usuario

    @discord.ui.button(label="Aprovar Registro",
                       style=discord.ButtonStyle.green,
                       custom_id="confirmar_recrutamento")
    async def confirmar(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        await interaction.response.send_message(
            f"✅ {self.usuario.mention} foi aprovado por {interaction.user.mention}!",
            ephemeral=False)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)


#aqui é o botão de criação fixo do chat
class RecrutarButtonView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Formulário de Recrutamento",
                       style=discord.ButtonStyle.green,
                       custom_id="abrir_recrutar")
    async def abrir_modal(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.send_modal(RecrutamentoModal())


#aqui é o botão de criação fixo do chat
class RecrutarAguiaButtonView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Formulário de Recrutamento Águia",
                       style=discord.ButtonStyle.green,
                       custom_id="abrir_recrutar_aguia")
    async def abrir_modal_aguia(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        await interaction.response.send_modal(RecrutamentoModalAguia())


#----------------- Modals -----------------#


#aqui é forms de recrutamento (espero que funcione)
class RecrutamentoModal(Modal, title="Formulário de Recrutamento"):
    nome = TextInput(label="Qual seu nome?",
                     placeholder="Digite seu nome",
                     required=True)
    id_jogo = TextInput(label="Qual seu ID no jogo?",
                        placeholder="Ex: 12345",
                        required=True)
    id_recrutador = TextInput(label="Qual o ID de quem te recrutou?",
                              placeholder="ID do recrutador",
                              required=True)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(IdDoCargo)

        novo_nome = f"APZ | {self.nome.value} | {self.id_jogo.value}"

        try:
            await member.edit(nick=novo_nome)
            nick_msg = f"✍️ Nickname alterado para: **{novo_nome}**"
        except discord.Forbidden:
            nick_msg = "⚠️ Não consegui alterar o nickname (verifique permissões do bot)."

        try:
            if role:
                await member.add_roles(role)
                role_msg = f"🎉 {member.mention} recebeu o cargo **{role.name}**!"
            else:
                role_msg = "⚠️ Cargo não encontrado."
        except discord.Forbidden:
            role_msg = "⚠️ Não consegui adicionar o cargo (verifique permissões do bot)."

        await interaction.response.send_message(
            f"✅ Recrutamento concluído!\n\n"
            f"**Nome:** {self.nome.value}\n"
            f"**ID Jogo:** {self.id_jogo.value}\n"
            f"**Recrutador:** {self.id_recrutador.value}\n\n"
            f"{nick_msg}\n{role_msg}",
            ephemeral=True)

        # Envia logs
        view = ConfirmacaoView(member)
        for canal_id in [IdDoCanalConfirmarRec, IdDoCanalLogs]:
            canal = guild.get_channel(canal_id)
            if canal:
                await canal.send(
                    f"📌 **Novo recrutamento registrado**\n"
                    f"Usuário: {member.mention} ({member.id})\n"
                    f"Nome: {self.nome.value}\n"
                    f"ID Jogo: {self.id_jogo.value}\n"
                    f"Recrutador: {self.id_recrutador.value}\n"
                    f"Cargo atribuído: {role.name if role else 'Não encontrado'}\n"
                    f"Nickname alterado: {novo_nome}",
                    view=view)


#esse aqui é o do aguia, antes tava todo bugado, ai separei os dois
class RecrutamentoModalAguia(Modal, title="Formulário de Recrutamento Águia"):
    nome = TextInput(label="Qual seu nome?",
                     placeholder="Digite seu nome",
                     required=True)
    id_jogo = TextInput(label="Qual seu ID no jogo?",
                        placeholder="Ex: 12345",
                        required=True)
    dia_prova = TextInput(label="Dia possível para seu curso",
                          placeholder="Ex: 22/09/2025",
                          required=True)

    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        await interaction.response.send_message(
            f"✅ Registro no **Curso Águia** concluído!\n\n"
            f"Nome: {self.nome.value}\n"
            f"ID Jogo: {self.id_jogo.value}\n"
            f"Dia do curso: {self.dia_prova.value}",
            ephemeral=True)

        canal_logs_aguia = guild.get_channel(IdDoCanalLogsAguia)
        if canal_logs_aguia:
            await canal_logs_aguia.send(
                f"🦅 **Novo registro no Curso Águia**\n"
                f"Usuário: {member.mention} ({member.id})\n"
                f"Nome: {self.nome.value}\n"
                f"ID Jogo: {self.id_jogo.value}\n"
                f"Dia do curso: {self.dia_prova.value}")


#----------------- Comandos -----------------#


#aqui o comando de setar o botão no chat
@bot.tree.command(name="botao_recrutar",
                  description="Envia o botão de recrutamento",
                  guild=discord.Object(id=IdDoServidor))
async def botao_recrutar(interaction: discord.Interaction):
    view = RecrutarButtonView()
    mensagem_descricao = (
        "Seja muito bem-vindo ao **Hospital Dubai**! 👋\n\n"
        "Clique no botão abaixo para se registrar, colocando:\n"
        "• Seu **nome**\n"
        "• Seu **ID no jogo**\n"
        "• O **ID do seu recrutador**")
    await interaction.response.send_message(mensagem_descricao, view=view)


#aqui o comando de setar o botão no chat aguia
@bot.tree.command(name="botao_recrutar_aguia",
                  description="Envia o botão do curso Águia",
                  guild=discord.Object(id=IdDoServidor))
async def botao_recrutar_aguia(interaction: discord.Interaction):
    view = RecrutarAguiaButtonView()
    mensagem = (
        "🦅 Seja muito bem-vindo ao **Curso Águia** do Hospital Dubai! 👋\n\n"
        "Clique no botão abaixo para se inscrever, colocando:\n"
        "• Seu **nome**\n"
        "• Seu **ID no jogo**\n"
        "• O **dia provável do curso**")
    await interaction.response.send_message(mensagem, view=view)


#----------------- Evento on ready -----------------#


#só pra ver se ta setando normal e sincronizando os comandos
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=IdDoServidor))
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")


# ----------------- Rodar bot ----------------- #
bot.run("Token-do-Bot")
