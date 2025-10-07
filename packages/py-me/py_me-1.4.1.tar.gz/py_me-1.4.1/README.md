# py_me

**py_me** é uma biblioteca Python que oferece módulos para manipulação de sons (`music_me`) e interfaces gráficas com Tkinter (`tk_me`).

## versão

**1.4.1** - *lançado em 6/10/2025*

**nome** - *musica sem volume, não da*

## mudanças

- adição de nome da verção
- adição de novas informações

## tk_me
### exemplo:
```python
    from py_me import tk_me

    aaa = tk_me.apenas_criar("oi", "100x100")
    def sair():
        aaa.destroy()
    tk_me.botão("sair", 0, 0, "Arial", 14, sair)
    aaa.mainloop()
```
### funções
- tk_import(nome_janela, tamanho_janela, arquivo_import)
- apenas_criar(nome_janela, tamanho_janela)
- label(texto, X1, Y1, fonte, tamanho)
- botão(texto, X1, Y1, fonte, tamanho, comando)
- janela_de_Texto(tamanho_X, tamanho_y, local_X, local_y)
- janela_error()
- destruir_objetos(objeto)
- tk_import_tk(nome_janela1, arquivo_tk, texto_label, texto_botão)
- slider(num_min, num_max, comando, X, Y)

## music_me
### exemplo
```python
    from py_me import music_me

    music_me.trilha_sonora_inloop(2, "minha\\batida.mp3")
    aaa = music_me.elemento_musical(1, "meu\\som.wav", 12)
    music_me.dell(aaa, 10)
```
    
### funções
- trilha_sonora_inloop(velocidade, arquivo)
- elemento_musical(velocidade, arquivo, tempo_a_esperar=0)
- elemento_musical_entonado(velocidade, entonacao, arquivo, tempo_a_esperar=0)
- dell(elemento, tempo_após_o_inicio_da_reprodução_para_o_del)
- stop(tempo)
- volume_elemento(som, volume, tempo)
- volume_geral(volume,  tempo)

## dependentes
- pygame
- pydub
    - FFmpeg

## Instalação

```bash
pip install py-me
