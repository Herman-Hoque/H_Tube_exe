#Autor: Herman Dantas Cabral Hoque
from time import sleep
from pytube import YouTube, Playlist
import pytube, json, yt_dlp, os
from flet import (app, Page, Divider, Column, Container, Row, TextButton,
                  Text, ElevatedButton, icons, IconButton, TextField,
                  FontWeight, padding, SafeArea, Theme, ColorScheme, Icon,
                  CrossAxisAlignment, Image, ThemeMode, ProgressBar,
                  ProgressRing, Stack, AppBar, AlertDialog, RadioGroup, Radio)

class HTube():
    def __init__(self, page):
        super().__init__()
        self.alt_url = 1
        self.yt_list = None
        self.page = page
        self.appBar = AppBar(toolbar_height=5)
        self.page.appbar = self.appBar

        self.caminho = os.path.join(os.path.expanduser('~'),'Downloads/%(title)s.%(ext)s')
        #self.caminho = '%(title)s.%(ext)s'
        self.caminho2 = os.path.join(os.path.expanduser('~'),'Downloads/%(title)s.mp3')
        #self.caminho2 = 'H_Tube(%(title)s).mp3'
        
        self.dev = AlertDialog(
            title=Text('Desenvolvedor'),
            content=Column(
                spacing=3,
                height=200,
                controls=[
                    Text('Dev: Herman Hoque', weight=FontWeight.BOLD),
                    Text('App: H_TUBE', weight=FontWeight.BOLD),
                    Text('Versão: 2.1', weight=FontWeight.BOLD),
                    Text('Instagram: \n   hprojects1401 \n   herman.cabral', weight=FontWeight.BOLD),
                    Text(),
                    ]
            )
        )

        #radio de seleção
        self.op_down = RadioGroup(
            value = 'video',
            content = Row(
                spacing = 10,
                controls=[
                    Radio(value='video', label='Vídeo'),
                    Radio(value='audio', label='Áudio')
                    ]                        
                )
            )

        self.btnLimpar = TextButton('Limpar', on_click=self.limpar)

        self.img = Image(
            src='/img/H_logo.png',
            width=180,
            height=180
        )

        self.nome_app = Container(
            content=Text('H_TUBE', size=20, weight=FontWeight.BOLD)
        )

        self.info1 = Container(
            content=Text('Baixar Vídeo, Áudio, Playlist do YouTube, Instagram, TikTok e outros',
                         size=11, weight=FontWeight.BOLD)
        )

        self.btnTema = IconButton(
            icon=icons.WB_SUNNY,
            on_click=self.mudar
        )

        self.btnDev = IconButton(
            icon=icons.CODE,
            on_click=self.show_dev
        )

        self.iconDown = Icon(name=icons.DOWNLOAD)
        self.percentagem = Text('')
        self.peso = Text('0 MB')
        # progresso
        self.progresso = Container()

        # area do link
        self.area_link = TextField(
            label='Link do Vídeo',
            hint_text='Digite ou cola o link aqui',
            border_radius=10,
            on_change=self.info_link
        )

        # botão Baixar
        self.btn_down = ElevatedButton('Baixar',
                                       color='#ffffff',
                                       bgcolor='#117EFF',
                                       width=250,
                                       on_click=self.baixar)
        # cabeçalho da app
        self.cab = Container(
            padding=padding.only(left=10, right=10),
            content=Column(
                spacing=2,
                controls=[
                    Stack(
                        controls=[
                            Row(
                                alignment='spaceBetween',
                                controls=[
                                    self.nome_app,
                                    Row(controls=[self.btnDev, self.btnTema])
                                ]
                            ),
                        ]
                    ),
                    self.info1
                ]
            )
        )

        # Corpo do programa a parte inferior
        self.corpo = Container(
            padding=padding.only(left=5, right=10),
            content=Column(
                spacing=5,
                controls=[
                    Container(
                        padding=padding.only(top=5, bottom=10),
                        content=Column(
                            controls=[
                                self.op_down,
                            ]
                        ) 

                    ),
                    
                    Container(
                        padding=padding.only(left=15, right=15),
                        content=self.area_link
                    ),
                    
                    Column(# img
                    	controls=[
                    		Container(
                                padding=padding.only(top=5, right=20), 
                                content=Row(
                                    alignment='end',
                                    controls=[self.btnLimpar])),
                    		Row(alignment='center', controls=[self.img])
                    	]
                    ),
                    Row(alignment='center', controls=[self.btn_down]),

                    self.progresso,
                    Row(alignment='center', controls=[
                        Text('Downloads localizados na pasta Download', size=12)])
                ]
            )
        )

        # conteudo da app no geral
        self.conteudo = Container(
            padding=padding.only(top=1),
            content=Column(
            	spacing=2,
                controls=[
                    self.cab,
                    # divisor
                    Divider(thickness=2, color='#117EFF'),
                    self.corpo
                ]
            )
        )

        with open('temas.json', 'r') as f:
            tema = json.load(f)
    
        if tema['tema'] == 'escuro':
            self.page.theme_mode = ThemeMode.DARK
            self.btnTema.icon = icons.WB_SUNNY
        else:
            self.page.theme_mode = ThemeMode.LIGHT
            self.btnTema.icon = icons.NIGHTLIGHT

        self.page.update()

    def show_dev(self, e):
        self.page.dialog = self.dev
        self.dev.open = True
        self.page.update()

    def limpar(self, e):
        self.area_link.value = None
        self.page.update()

    def miniatura(self, mini):
        self.img.src = mini
        self.page.update()

    #metodo do progresso de download
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            self.percentagem.value = f'           {d["_percent_str"]}'
            self.peso.value = f'{d["_total_bytes_str"]}'     
            
        elif d['status'] == 'finished':

            try: # caso seja playlist
                #passar para a proxima miniatura e título dos videos da playlist
                self.info_link_list(self.yt_list.video_urls[self.alt_url])
                self.alt_url += 1
                self.msgDown.value = f'Baixando {self.alt_url}º...'
                self.percentagem.value = ''
                print('Download concluído.')
            except:#caso seja video normal
                print('Download concluído.')
        self.page.update()  

    # baixar os vídeos
    def baixar(self, e):
        self.area_link.error_text = ''
        self.msgDown = Text('Baixando...')
        # barra de progresso
        self.load = ProgressBar(width=150, color='#117EFF',
                                bgcolor='#eeeeee')
        self.page.update()
        try:
            # se tiver link faz isso
            if self.area_link.value:
                self.btn_down.disabled = True
                self.percentagem.value = ''
                self.infoDown = Text('A procurar vídeo...', size=13)
                self.progresso.content = Row(
                    alignment='center',
                    controls=[ProgressRing(width=14, height=14),
                              self.infoDown
                              ]
                )
                self.page.update()
                sleep(1)
                # Caso queira baixar vídeo
                if self.op_down.value == 'video':
                    print('opção vídeo')
                    down_opts = {
                        'format': 'best',
                        'outtmpl': self.caminho,
                        'progress_hooks': [self.progress_hook],
                        'noplaylist': False
                        }

                    self.infoDown.value = 'A filtrar link...'
                    self.progresso.update()
                    with yt_dlp.YoutubeDL(down_opts) as ydl:
                        self.progresso.content = Row(
                        alignment='center',
                        controls=[
                            self.iconDown,

                            Column(
                                controls=[
                                    Row(
                                        spacing=35,
                                        controls=[self.msgDown, self.peso]
                                    ),

                                    self.load,
                                    self.percentagem
                                    ]
                                )
                            ]
                        )
                        # Faz o download
                        ydl.download([self.area_link.value])

                # Caso audio
                if self.op_down.value == 'audio':
                    print('opção audio')
                    down_opts = {
                        'format': 'bestaudio/best',  
                        'outtmpl': self.caminho2,
                        'progress_hooks': [self.progress_hook],
                    }
                    self.infoDown.value = 'A filtrar link...'
                    self.progresso.update()
                    with yt_dlp.YoutubeDL(down_opts) as ydl:
                        self.progresso.content = Row(
                        alignment='center',
                        controls=[
                            self.iconDown,

                            Column(
                                controls=[
                                    Row(
                                        spacing=35,
                                        controls=[self.msgDown, self.peso]
                                    ),

                                    self.load,
                                    self.percentagem
                                    ]
                                )
                            ]
                        )
                        self.msgDown.value = f'Baixando áudio...'
                        ydl.download([self.area_link.value])
                                       

                self.msgDown.value = 'Concluído'
                self.load.value = 100
                print('Concluído')

            else:
                self.area_link.error_text = 'Informe o link por favor!'
                print('sem link')

        #Erro de internet
        except yt_dlp.utils.DownloadError:
            self.progresso.content = Row(alignment='center', controls=[Text('Erro ao baixar, verifique o link ou a internet!',
                                                                         size=12, color='#ff0000')])                
        #outros erros
        except Exception as e:
            self.progresso.content = Row(scroll=True, alignment='center', controls=[Text(f'Erro: {e}',
                                                                            size=12, color='#ff0000')])
        self.btn_down.disabled = False
        self.alt_url = 1
        self.page.update()

    # Mudar o tema da app

    def mudar(self, e):

        if self.page.theme_mode == ThemeMode.DARK:
            with open('temas.json', 'w') as f:
                json.dump({"tema":"claro"}, f)
            self.page.theme_mode = ThemeMode.LIGHT
            self.btnTema.icon = icons.NIGHTLIGHT
        else:
            with open('temas.json', 'w') as f:
                json.dump({"tema":"escuro"}, f)
            self.page.theme_mode = ThemeMode.DARK
            self.btnTema.icon = icons.WB_SUNNY

        self.page.update()

    #altera a miniatura e titulo de uma playlist
    def info_link_list(self, url):
        yt = YouTube(url)                    
        mini = yt.thumbnail_url
        self.btn_down.text = yt.title
        self.miniatura(mini)
        

    def info_link(self, e):
        try:

            try: #tenta isso se for playlist
                self.yt_list = Playlist(self.area_link.value)
                self.info_link_list(self.yt_list.video_urls[0])
                
            except: #se for apenas um vídeo                   
                yt = YouTube(self.area_link.value)
                mini = yt.thumbnail_url
                self.btn_down.text = yt.title
                self.miniatura(mini)

        except:
            self.img.src = '/img/H_logo.png'
            self.btn_down.text = 'Baixar'
        self.page.update()


def main(page: Page):

    page.title = 'H_tube'
    page.window_width = 650
    page.window_height = 650
    page.window_maximizable = False
    page.theme = Theme(color_scheme=ColorScheme(primary='#117EFF'))
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    page.padding = 0
    page.scroll = 'adaptive'

    page.add(
        SafeArea(
            HTube(page).conteudo

        )
    )

    page.update()


app(target=main, assets_dir='/assets')
