# inSPECT — Controle de Qualidade de Sistemas SPECT

Aplicativo desktop em Python para análise de imagens de controle de qualidade de sistemas SPECT a partir de arquivos DICOM. A interface permite executar análises intrínsecas ou extrínsecas, visualizar gráficos e ROIs e, quando há aquisições estática e dinâmica, executar o teste de temporização.

> **Aviso:** este aplicativo é uma ferramenta de pesquisa e controle de qualidade. Não se destina a diagnóstico clínico. Valide os métodos e resultados de acordo com o protocolo aplicável antes de utilizá-los.

## Funcionalidades

- Análise de aquisição intrínseca (sem colimador) ou extrínseca (com colimador).
- Seleção de arquivos DICOM estático e dinâmico.
- Exibição de histogramas e imagens do fantoma/ROI.
- Teste de temporização quando são fornecidas ambas as aquisições.
- Seleção independente das tags DICOM de duração estática e dinâmica.
- Opções para salvar imagens e relatórios no diretório configurado.
- Execução de análise de imagem com apenas um arquivo. Nesse caso, o teste de temporização é omitido e a interface informa que são necessárias as aquisições estática e dinâmica.

# Instalação no Windows

O inSPECT é distribuído como um aplicativo portátil. **Não é necessário instalar Python**. Baixe e extraia a pasta do aplicativo.

### 1. Baixar o aplicativo

1. Abra a página do projeto no GitHub.
2. Selecione **Releases**.
3. Abra a versão desejada e baixe o arquivo ZIP do aplicativo para Windows, por exemplo, `inSPECT-Windows.zip`.
4. Aguarde o download terminar.

Baixe o ZIP publicado em **Releases**. Não baixe o código-fonte (`Source code`) para instalar o aplicativo.

### 2. Extrair os arquivos

1. Abra a pasta **Downloads** no Explorador de Arquivos.
2. Clique com o botão direito no ZIP baixado.
3. Selecione **Extrair Tudo...** e confirme a extração.
4. Mova a pasta extraída para um local permanente, por exemplo:

   `Documentos\inSPECT`

   Não execute o aplicativo diretamente de dentro do arquivo ZIP. Mantenha juntos todos os arquivos e subpastas extraídos — o executável pode depender deles.

### 3. Abrir o inSPECT

1. Abra a pasta extraída.
2. Abra a subpasta `inSPECT`, se houver.
3. Dê dois cliques em `inSPECT.exe`.

Se o Windows mostrar um aviso de segurança, confirme com o suporte de TI do hospital antes de prosseguir. Não ignore avisos de segurança se não tiver certeza de que baixou o arquivo da página oficial do projeto.

### 4. Criar um atalho (opcional)

Na pasta extraída, clique com o botão direito em `inSPECT.exe` e escolha **Mostrar mais opções > Enviar para > Área de trabalho (criar atalho)**, se essas opções estiverem disponíveis no Windows.

### 5. Primeira análise

1. Em **Configurações**, confira as tags de duração selecionadas para as aquisições estática e dinâmica. As tags corretas dependem do equipamento e dos dados DICOM utilizados.
2. Selecione os arquivos DICOM no aplicativo.
3. Escolha o tipo de aquisição: Intrínseca (sem colimador) e Extrínseca (com colimador). Escolha se deseja guardar os resultados como arquivos no computador.
4. Clique em **Calcular**.

O teste de temporização só pode ser executado quando forem fornecidos os arquivos estático e dinâmico. A análise de imagem pode ser executada com apenas um arquivo, mas nesse caso o teste de temporização não será realizado.

Configure o diretório de saída em **Configurações**. Se não tiver permissão para gravar na pasta do aplicativo, escolha uma pasta em **Documentos**.

### Atualizar ou remover o aplicativo

Para atualizar, baixe e extraia a nova versão em uma pasta nova. Mantenha seus relatórios e imagens salvos fora da pasta antiga antes de removê-la.

Para remover o aplicativo, feche-o e exclua a pasta extraída. Isso não remove cópias de relatórios ou imagens que você salvou em outros locais.

### Privacidade e segurança dos dados

Arquivos DICOM podem conter informações pessoais e de saúde. Siga as regras de privacidade e segurança da sua instituição. Não envie arquivos de pacientes por e-mail nem os publique no GitHub. Use apenas dados autorizados e devidamente anonimizados para testes.


## Manual de Uso
Em Configurações, escolha as tags que armazenam a duração das aquisições estática e dinâmica. As opções iniciais são (0018,1242) para estática e (0011,100B) para dinâmica.
Selecione os arquivos DICOM. É possível digitar o caminho ou usar Procurar.
Selecione Aquisição Intrínseca ou Aquisição Extrínseca.
Escolha se deseja salvar imagens e relatório e configure o diretório de saída, se necessário.
Clique em Calcular.
Para iniciar outra análise, clique em Iniciar Nova Análise.
O teste de temporização só é executado quando ambos os arquivos são informados. Se uma tag selecionada estiver ausente ou contiver uma duração inválida, o aplicativo apresenta um erro; ele não substitui automaticamente o valor por outra tag.

Tags de duração
As tags disponíveis na interface são:

(0018,9073)
(0018,9220)
(0018,1242)
(0018,1063)
(0018,1065)
(0011,100B)
A conversão de unidades depende da implementação correspondente em funções_para_app.py e do significado da tag. Confirme a tag e as unidades usadas pelo equipamento; não presuma que todos os fabricantes armazenam a duração da mesma forma.

Gerar um executável Windows
Instale o PyInstaller no mesmo ambiente virtual e crie primeiro uma versão em pasta:
```
.\.venv\Scripts\python.exe -m pip install pyinstaller

.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --name inSPECT `
  --collect-all scipy `
  --collect-all matplotlib `
  --collect-all pydicom `
  --collect-all cv2 `
  --hidden-import "funções_para_app" `
  ".\inSPECT Controle de Qualidade de Sistemas SPECT.py"
```
O executável será criado em:
```
dist\inSPECT\inSPECT.exe
```

## Privacidade e dados de exemplo
Não publique arquivos DICOM reais que possam conter dados pessoais ou informações de saúde. Antes de compartilhar dados de teste, confirme que estão devidamente anonimizados e que você tem autorização para distribuí-los. Não inclua ambientes virtuais, arquivos temporários de build ou resultados de pacientes no repositório.

## Contribuições e contato
Para relatar problemas ou sugerir melhorias, abra uma issue no GitHub ou envie feedback para inspect.cq@gmail.com.

Desenvolvido por Emilie Chen para projeto de Iniciação Científica da Universidade Federal do ABC, São Bernardo do Campo, Brasil.
