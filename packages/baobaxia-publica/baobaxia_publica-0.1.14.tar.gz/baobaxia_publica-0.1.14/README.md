# baobaxia-publica


<pre>
                               .
                              ,d              .   ,
                             aA...             YF^
                              *@@@b          d@P
                                *@@@b,,,,,-d@@P   ,     ,
                    ....a@@@@aa.. *@@V@`;;..,,  ,*,   ,*
                     `V*'  ``*@@B`b b@((bb`@@P*q*@@*"'
                               `*@`9@,(()))*'   `*.   
                                `A@,`@@Y@(;'
                                 (a`@,`@`&@
                                ."@,@`.@(@@
                               (@a.@",@^a.,
                               ,.o..o@ (@o.`
                               (*",.`*@@o`*@,         <i>"Vamos fazer um mundo digital</i>
                              ,',@***@a,,`^*.,                       <i>mais do nosso jeito!"</i>
                              ,&^,@@@@@a,`a.,
                              &`@`,;aaaa @; )@        <a href="http://wiki.mocambos.net/wiki/NPDD">NPDD/Rede Mocambos</a>
                              c@(.@".;'".@",@@"
                              @@ @",@`.@*`,@@`,
                              @P,@,*@a, ,a@*`,@
                            , *(`*@@a.,*@*`,@*`
                ,;a&*"` .;a@@ *;,'o,`*@@a;@@P`, oo..,,
        ,.;a@@@*"`  ,;a@@*"` , *"`7`,"a,`"*",d) **oo..`""*oo.,
    ,;@@@@@@*`  ,;d@@@@P` ,.@@b *@b`"@a,`"*@@@` ~*o..,`""*oo,."*@a,
    @@@@@@@@b   `*@@@@@;, `'"*@, "*@@a`*@@&;,` ~*o.,, `"@a, `*@b,`*@a
    `"*@@@@@@b.    `"*o@@@@a;,  `"*o,,`` `""*@@@b;.`"*, `@@   `@@;  `*,
       `"*@@@@@@b.     ``*o@@@@@@;,   `"*ooo**'`  ,;o@*  `@    @@@; 
          `"*@@@@@@@b.,     ``"***oo@@oo;,,,,,;;o@@*'` ,;o@    `@@@@,
             `"*@@@@@@@@@b.,,                       ,;o@@@@     @@@@@ 
                `"*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@P*    ,@@@@@
                        ````````''''''''''''''''''''```  ,...;@@@@P*`
                                                      ```'"""```
</pre>

Ferramenta de linha de comando para publicar mídias e artigos no **Baobáxia** via API.

## Instalação

Com [pipx](https://pipx.pypa.io/):

```bash
pipx install baobaxia-publica
```

Ou manualmente (no diretório do código):

```bash
pip install .
```

## Uso

```bash
publica [opções] caminho...
```

O parâmetro `caminho` pode ser:  
- Um ou mais **arquivos locais** (imagens, vídeos, áudios, markdown);  
- Um **link de YouTube** (será baixado e publicado como mídia automaticamente).  

## Exemplos

Enviar uma imagem:  
```bash
publica --usuario vince --senha livre ~/imagens/foto.png
```

Enviar várias imagens de uma vez:  
```bash
publica --usuario vince --senha livre ~/imagens/*.jpg
```

Enviar um artigo Markdown:  
```bash
publica --usuario vince --senha livre --titulo "Meu artigo" --descricao "teste" artigo.md
```

Publicar um vídeo direto do YouTube:  
```bash
publica --usuario vince --senha livre "https://www.youtube.com/watch?v=XXXX"
```

## Opções

| Opção           | Descrição |
|-----------------|-----------|
| `--url`         | URL da API (default: `https://baobaxia.net/api/v2`) |
| `--usuario`     | Usuário para autenticação |
| `--senha`       | Senha do usuário |
| `--galaxia`     | SMID da galáxia de destino |
| `--mucua`       | SMID da mucua de destino |
| `--titulo`      | Título do post (obrigatório se não interativo) |
| `--descricao`   | Descrição do post |
| `--tags`        | Lista de tags separada por vírgulas) |
| `--status`      | Status do conteúdo (default: `draft`) |
| `--language`    | Idioma do conteúdo |
| `--rights`      | Direitos autorais |
| `--date`        | Data de publicação |
| `--publisher`   | Nome do publicador |
| `--contributor` | Lista de contribuidores separados por vírgula |
| `--relation`    | Relação (referências) |
| `--mocambo`     | Nome do mocambo |
| `--insecure`    | Ignora verificação SSL |
| `--qualidade`   | Qualidade de vídeo ao baixar do YouTube (`baixa`, `media`, `alta` [default], `max`) |

## Ajuda

Para ver todas as opções diretamente no terminal:  

```bash
publica -h
```
