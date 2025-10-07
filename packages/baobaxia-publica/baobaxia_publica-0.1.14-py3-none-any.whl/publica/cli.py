#!/usr/bin/env python3
import argparse
import requests
import os
import mimetypes
import getpass
from pathlib import Path
import urllib3
from tqdm import tqdm
from . import __version__
import uuid
import subprocess
import tempfile
import json
import shutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --------- Utils ---------
def guess_type(filename):
    mtype, _ = mimetypes.guess_type(filename)
    if not mtype:
        return "arquivo"
    if mtype.startswith("image"):
        return "imagem"
    if mtype.startswith("video"):
        return "video"
    if mtype.startswith("audio"):
        return "audio"
    if mtype == "text/markdown":
        return "artigo"
    return "arquivo"

def guess_type_from_url(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        ctype = resp.headers.get("Content-Type")
        if ctype:
            ctype = ctype.split(";")[0].strip()
            if ctype.startswith("image"):
                return "imagem"
            if ctype.startswith("video"):
                return "video"
            if ctype.startswith("audio"):
                return "audio"
            if ctype in ("text/markdown", "text/x-markdown"):
                return "artigo"
        return guess_type(url)
    except Exception:
        return guess_type(url)

def autenticar(api_url, usuario, senha, verify=True):
    resp = requests.post(
        f"{api_url}/token",
        data={"username": usuario, "password": senha},
        verify=verify
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def listar_galaxias(api_url, token, verify=True):
    resp = requests.get(f"{api_url}/galaxia", headers={"Authorization": f"Bearer {token}"}, verify=verify)
    resp.raise_for_status()
    return resp.json()

def escolher_galaxia_mucua(api_url, token, galaxia_arg=None, mucua_arg=None, verify=True):
    galaxias = listar_galaxias(api_url, token, verify)
    if not galaxia_arg:
        print("== Galaxias disponíveis ==")
        for i, g in enumerate(galaxias):
            nome = g.get("name") or g.get("slug") or str(g)
            print(f"{i+1}. {nome} ({g.get('slug')})")
        idx = int(input("Escolha a galaxia: ")) - 1
        galaxia = galaxias[idx]["slug"]
        mucua = galaxias[idx].get("default_mucua")
    else:
        galaxia = galaxia_arg
        mucua = mucua_arg
    if not mucua:
        print("⚠️ Nenhuma mucua listada, usando default_mucua.")
        mucua = galaxias[0].get("default_mucua")
    return galaxia, mucua

# --------- Criação ---------
def criar_midia(api_url, token, galaxia, mucua, titulo, descricao=None, tipo="arquivo", extra=None, verify=True):
    url = f"{api_url}/{galaxia}/{mucua}/acervo/midia"
    payload = {
        "title": titulo,
        "description": descricao or "",
        "type": tipo,
        "is_public": True,
    }
    if extra:
        payload.update(extra)
    if "tags" in payload and isinstance(payload["tags"], str):
        payload["tags"] = [t.strip() for t in payload["tags"].split(",") if t.strip()]
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, verify=verify)
    if not resp.ok:
        print(f"❌ Erro criar mídia: {resp.text}")
    resp.raise_for_status()
    midia = resp.json()
    print(f"🎞️ Mídia criada ({tipo}): {titulo}")
    return midia

def criar_artigo(api_url, token, galaxia, mucua, titulo, descricao=None, extra=None, verify=True):
    url = f"{api_url}/{galaxia}/{mucua}/blog/artigo"
    payload = {
        "title": titulo,
        "description": descricao or "",
        "is_public": True,
    }
    if extra:
        payload.update(extra)
    if "tags" in payload:
        if isinstance(payload["tags"], list):
            payload["tags"] = ", ".join(payload["tags"])
        elif isinstance(payload["tags"], str):
            payload["tags"] = ", ".join([t.strip() for t in payload["tags"].split(",") if t.strip()])
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, verify=verify)
    if not resp.ok:
        print(f"❌ Erro criar artigo: {resp.text}")
    resp.raise_for_status()
    artigo = resp.json()
    print(f"📝 Artigo criado: {titulo}")
    return artigo

# --------- Upload ---------

def upload_arquivo(api_url, token, galaxia, mucua, smid, caminho, tipo="midia", verify=True):
    url = (
        f"{api_url}/{galaxia}/{mucua}/acervo/upload/{smid}"
        if tipo == "midia"
        else f"{api_url}/{galaxia}/{mucua}/blog/content/{smid}"
    )
    file_size = os.path.getsize(caminho)
    filename = os.path.basename(caminho)
    boundary = uuid.uuid4().hex

    # cabeçalho do multipart
    preamble = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="arquivo"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode()

    # final do multipart
    closing = f"\r\n--{boundary}--\r\n".encode()

    total_size = len(preamble) + file_size + len(closing)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    def gen():
        # manda cabeçalho
        yield preamble
        sent = 0
        with open(caminho, "rb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, unit_divisor=1024,
            desc=filename
        ) as bar:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):  # 1MB
                sent += len(chunk)
                bar.update(len(chunk))
                yield chunk
            bar.update(len(closing))
            yield closing

    resp = requests.post(url, headers=headers, data=gen(), verify=verify)

    if not resp.ok:
        print(f"❌ Erro upload {tipo}: {resp.text}")
    else:
        print(f"✅ Upload concluído: {filename}")
    resp.raise_for_status()


def upload_arquivo_url(api_url, token, galaxia, mucua, smid, url_remota, verify=True):
    endpoint = f"{api_url}/{galaxia}/{mucua}/acervo/upload/{smid}"
    resp = requests.post(endpoint, headers={"Authorization": f"Bearer {token}"}, params={"url": url_remota}, verify=verify)
    if not resp.ok:
        print(f"❌ Erro upload via URL: {resp.text}")
    else:
        print(f"✅ Upload remoto concluído: {url_remota}")
    resp.raise_for_status()

# --------- Extras ---------
def coletar_extra(args, tipo):
    extra = {}
    campos = ["tags","status","is_public","language","rights","date","publisher","contributor","relation","location","mocambo"]
    for campo in campos:
        val = getattr(args, campo, None)
        if val:
            if campo == "tags":
                tags = [t.strip() for t in val.split(",") if t.strip()]
                extra["tags"] = ", ".join(tags) if tipo == "artigo" else tags
            elif campo == "contributor":
                extra["contributor"] = val if isinstance(val, list) else [c.strip() for c in val.split(",") if c.strip()]
            elif campo == "is_public":
                extra["is_public"] = val.lower() in ("true","1","yes","sim") if isinstance(val, str) else bool(val)
            else:
                extra[campo] = val
    return extra

def perguntar_atributos_interativos():
    extra = {}
    while True:
        print("\n== Atributos extras ==")
        print("1. Tags")
        print("2. Status")
        print("3. Publisher")
        print("4. Contributor")
        print("5. Language")
        print("6. Rights")
        print("7. Relation")
        print("8. Location")
        print("9. Mocambo")
        print("0. Finalizar")
        escolha = input("Escolha um atributo (0 para sair): ").strip()
        if escolha == "0":
            break
        if escolha == "1": extra["tags"] = input("🏷️ Tags (separadas por vírgula): ").strip()
        elif escolha == "2": extra["status"] = input("📌 Status: ").strip()
        elif escolha == "3": extra["publisher"] = input("🏛️ Publisher: ").strip()
        elif escolha == "4": extra["contributor"] = input("👥 Contributors (vírgula): ").strip()
        elif escolha == "5": extra["language"] = input("🌐 Language: ").strip()
        elif escolha == "6": extra["rights"] = input("⚖️ Rights: ").strip()
        elif escolha == "7": extra["relation"] = input("🔗 Relation: ").strip()
        elif escolha == "8": extra["location"] = input("📍 Location: ").strip()
        elif escolha == "9": extra["mocambo"] = input("🏘️ Mocambo: ").strip()
    return extra

# --------- Conversão de Vídeo ---------
def converter_video_para_mp4(caminho_entrada, qualidade="alta", tmpdir=None):
    """
    Converte vídeo para MP4 usando ffmpeg
    """
    if tmpdir is None:
        tmpdir = tempfile.mkdtemp(prefix="publica-convert-")
    
    nome_base = os.path.splitext(os.path.basename(caminho_entrada))[0]
    caminho_saida = os.path.join(tmpdir, f"{nome_base}.mp4")
    
    # Configurações de qualidade baseadas no parâmetro
    qual_map = {
        "baixa": ["-crf", "28", "-preset", "fast"],
        "media": ["-crf", "23", "-preset", "medium"], 
        "alta": ["-crf", "18", "-preset", "slow"],
        "max": ["-crf", "15", "-preset", "veryslow"]
    }
    
    args_qualidade = qual_map.get(qualidade, qual_map["alta"])
    
    # Comando ffmpeg para conversão
    cmd = [
        "ffmpeg", "-i", caminho_entrada,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        *args_qualidade,
        "-y",  # Sobrescrever arquivo se existir
        caminho_saida
    ]
    
    print(f"🔄 Convertendo {os.path.basename(caminho_entrada)} para MP4 ({qualidade})...")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Conversão concluída: {os.path.basename(caminho_saida)}")
        return caminho_saida, tmpdir
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na conversão: {e}")
        print(f"stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None, tmpdir
    except FileNotFoundError:
        print("❌ ffmpeg não encontrado. Instale com: sudo apt install ffmpeg")
        return None, tmpdir

def precisa_converter(caminho):
    """
    Verifica se o arquivo precisa de conversão para MP4
    """
    ext = os.path.splitext(caminho)[1].lower()
    # Formatos que devem ser convertidos para MP4
    formatos_para_converter = ['.avi', '.mpg', '.ogv', '.ogg', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.3gp']
    return ext in formatos_para_converter

# --------- Processamento ---------
def carregar_arquivos(caminhos, qualidade="alta"):
    arquivos = []
    tmpdirs_conversao = []
    
    for c in caminhos:
        p = Path(c).expanduser()
        if p.is_dir():
            arquivos_encontrados = list(p.rglob("*"))
        else:
            arquivos_encontrados = [p]
            
        for arquivo in arquivos_encontrados:
            if arquivo.is_file():
                arquivo_str = str(arquivo)
                # Verificar se precisa converter
                if guess_type(arquivo_str) == "video" and precisa_converter(arquivo_str):
                    print(f"🎥 Arquivo de vídeo detectado: {os.path.basename(arquivo_str)}")
                    if input(f"❓ Converter {os.path.basename(arquivo_str)} para MP4? [S/n]: ").strip().lower() in ("", "s", "sim", "y", "yes"):
                        convertido, tmpdir = converter_video_para_mp4(arquivo_str, qualidade)
                        if convertido:
                            arquivos.append(convertido)
                            tmpdirs_conversao.append(tmpdir)
                        else:
                            # Se a conversão falhou, usar o original
                            arquivos.append(arquivo_str)
                    else:
                        arquivos.append(arquivo_str)
                else:
                    arquivos.append(arquivo_str)
    
    return arquivos, tmpdirs_conversao

def processar(api_url, arquivos, token, galaxia, mucua, titulo, descricao, args, verify=True):
    grupos = {}
    for arq in arquivos:
        tipo = guess_type(arq)
        if tipo == "artigo":
            extra = coletar_extra(args, "artigo")
            sugestao = os.path.splitext(os.path.basename(arq))[0]
            t = titulo or input(f"📝 Título para artigo '{os.path.basename(arq)}' [{sugestao}]: ").strip() or sugestao
            d = descricao or input(f"📝 Descrição opcional para '{t}' (Enter para pular): ").strip() or None
            artigo = criar_artigo(api_url, token, galaxia, mucua, titulo=t, descricao=d, extra=extra, verify=verify)
            smid = artigo.get("smid")
            upload_arquivo(api_url, token, galaxia, mucua, smid, arq, tipo="artigo", verify=verify)
        else:
            grupos.setdefault(tipo, []).append(arq)
    for tipo, lista in grupos.items():
        extra = coletar_extra(args, "midia")
        sugestao = f"{tipo.capitalize()}s"
        t = titulo or input(f"🎞️ Título para grupo '{tipo}' ({len(lista)} arquivos) [{sugestao}]: ").strip() or sugestao
        d = descricao or input(f"📝 Descrição opcional para grupo '{t}' (Enter para pular): ").strip() or None
        midia = criar_midia(api_url, token, galaxia, mucua, t, descricao=d, tipo=tipo, extra=extra, verify=verify)
        smid = midia.get("smid")
        for arq in lista:
            upload_arquivo(api_url, token, galaxia, mucua, smid, arq, tipo="midia", verify=verify)

# --------- yt-dlp ---------
def baixar_com_yt_dlp(url, qualidade="alta"):
    qual_map = {
        "baixa": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "media": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "alta": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "max": "bestvideo+bestaudio/best",
    }
    fmt = qual_map.get(qualidade, qual_map["alta"])
    tmpdir = tempfile.mkdtemp(prefix="publica-yt-")
    outtmpl = os.path.join(tmpdir, "%(title).200s.%(ext)s")
    subprocess.run(["yt-dlp","-f",fmt,"--merge-output-format","mp4","--write-info-json","-o",outtmpl,url], check=True)
    files = [str(p) for p in Path(tmpdir).iterdir() if p.is_file()]
    info_file = next((f for f in files if f.endswith(".info.json")), None)
    titulo, descricao = None, None
    if info_file:
        with open(info_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            titulo, descricao = data.get("title"), data.get("description")
    media_files = [f for f in files if os.path.splitext(f)[1].lower() in [".mp4",".mkv",".webm",".mov",".avi",".flv",".mp3",".ogg"]]
    return media_files, titulo, descricao, tmpdir

# --------- Main ---------
def main():
    print("")
    print("🌳 \033[91mBA\033[93mOBÁ\033[92mXIA\033[0m Publica ☄")
    print("")
    print("🪘 🏝  🛖 To voltando pra casa com um pé de baobá.. 🌱")
    print("")
    print("🌎 \033[1;36mcompartilha\033[0m sua  🛶 viagem 🌟 nas galaxias 🪐")
    print("")

    parser = argparse.ArgumentParser(
        description="Ferramenta para upload de arquivos para a rede Baobáxia")                                                                                                                        
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("caminho",
                        nargs="+",
                        help="Arquivos, pastas ou URLs para enviar")

    # Opções de conexão e autenticação
    parser.add_argument("--url", "--api-url", dest="url",
                        default="https://baobaxia.net/api/v2",
                        help="URL da API (default: %(default)s)")
    parser.add_argument("--usuario", help="Usuário para autenticação")
    parser.add_argument("--senha", help="Senha do usuário")
    parser.add_argument("--insecure", action="store_true",
                        help="Ignora verificação SSL")

    # Opções de destino
    parser.add_argument("--galaxia", help="SMID da galáxia de destino")
    parser.add_argument("--mucua", help="SMID da mucua de destino")
    parser.add_argument("--mocambo", help="Nome do mocambo")

    # Metadados do conteúdo
    parser.add_argument("--titulo",
                        help="Título do post (obrigatório se não interativo)")
    parser.add_argument("--descricao", help="Descrição do post")
    parser.add_argument("--tags",
                        help="Lista de tags separadas por vírgula")
    parser.add_argument("--status", default="draft", 
                        help="Status do conteúdo (default: %(default)s)")
    parser.add_argument("--language", help="Idioma do conteúdo")
    parser.add_argument("--rights", help="Direitos autorais")
    parser.add_argument("--date", help="Data de publicação")
    parser.add_argument("--publisher", help="Nome do publicador")
    parser.add_argument("--contributor", help="Lista de contribuidores separados por vírgula")
    parser.add_argument("--relation", help="Relação (referências)")
    parser.add_argument("--location", help="Localização formato: lat,long");

    # Opções de qualidade
    parser.add_argument("--qualidade", choices=["baixa", "media", "alta", "max"], 
                        default="alta", 
                        help="Qualidade para conversão de vídeo e download do YouTube (default: %(default)s)")
    
    args = parser.parse_args()
    
    api_url = args.url or input("🌐 URL da API [https://baobaxia.net/api/v2]: ").strip() or "https://baobaxia.net/api/v2"
    verify = not args.insecure
    if "baobaxia.net" in api_url: verify = False
    usuario = args.usuario or input("👤 Usuário: ")
    senha = args.senha or getpass.getpass("🔑 Senha: ")
    token = autenticar(api_url, usuario, senha, verify=verify)
    galaxia, mucua = escolher_galaxia_mucua(api_url, token, args.galaxia, args.mucua, verify=verify)

    # Perguntar extras antes de criar mídias
    campos_passados = any([args.tags,args.status,args.publisher,args.contributor,args.language,args.rights,args.relation,args.location,args.mocambo])
    if not campos_passados:
        if input("❓ Deseja adicionar atributos extras? [s/N]: ").strip().lower() == "s":
            extra_interativos = perguntar_atributos_interativos()
            for k,v in extra_interativos.items(): setattr(args,k,v)

    tmpdirs, tmpdirs_conversao, caminhos_para_carregar = [], [], []
    for entrada in args.caminho:
        if entrada.startswith("http://") or entrada.startswith("https://"):
            if "youtube.com" in entrada or "youtu.be" in entrada:
                files, yt_title, yt_desc, tmpdir = baixar_com_yt_dlp(entrada, qualidade=args.qualidade)
                if yt_title and not args.titulo: args.titulo = yt_title
                if yt_desc and not args.descricao: args.descricao = yt_desc
                caminhos_para_carregar.extend(files); tmpdirs.append(tmpdir)
            else:
                tipo = guess_type_from_url(entrada)
                if tipo == "arquivo":
                    escolha = input(f"❓ Tipo da URL '{entrada}' não detectado. [imagem/video/audio/artigo/arquivo]: ").strip().lower()
                    tipo = {"imagem":"imagem","video":"video","audio":"audio","artigo":"artigo"}.get(escolha,"arquivo")
                extra = coletar_extra(args, "midia")
                t = args.titulo or input(f"🎞️ Título para a mídia (URL {entrada}): ").strip() or os.path.basename(entrada.split('?')[0]) or entrada
                d = args.descricao
                midia = criar_midia(api_url, token, galaxia, mucua, t, descricao=d, tipo=tipo, extra=extra, verify=verify)
                smid = midia.get("smid")
                upload_arquivo_url(api_url, token, galaxia, mucua, smid, entrada, verify=verify)
        else:
            caminhos_para_carregar.append(entrada)

    # Carregar arquivos com possível conversão
    arquivos, tmpdirs_conversao = carregar_arquivos(caminhos_para_carregar, args.qualidade)
    
    if arquivos: 
        processar(api_url, arquivos, token, galaxia, mucua, args.titulo, args.descricao, args, verify=verify)
    
    # Limpeza de diretórios temporários
    for td in tmpdirs + tmpdirs_conversao: 
        shutil.rmtree(td, ignore_errors=True)

if __name__ == "__main__": 
    main()
