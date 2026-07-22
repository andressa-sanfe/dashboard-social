
## 🎯 Objetivos
O dashboard foi projetado para atender aos seguintes pontos estratégicos do time de Social:

1. **Acompanhamento de Conteúdo Qualitativo:** Medir o valor real que os conteúdos geram para o público (conteúdo educativo, viral, inspirador).
2. **Monitoramento da Saúde da Comunidade:** Avaliar a agilidade no atendimento (SLA) e a percepção da marca (análise de sentimento).
3. **Desempenho Orgânico vs. Pago:** Isolar dados orgânicos provenientes de páginas do **Facebook** e **Instagram** para entender o alcance genuíno da marca.
4. **Tomada de Decisão Criativa:** Identificar quais formatos (Reels, Carrossel, Imagem Única) e editorias de conteúdo apresentam os melhores índices de retenção e salvamentos.

## 📐  KPIs Mapeados

O painel reúne indicadores divididos em três pilares fundamentais para o time de Social:

### 1. Ressonância e Qualidade do Conteúdo
* **Taxa de Salvamento (*Save Rate*):** Indicador de conteúdo útil ou informativo que o usuário guarda para consultar depois.
* **Taxa de Compartilhamento (*Share Rate*):** Indicador de viralidade e defesa/recomendação da marca.
* **Retenção de Vídeo (*Completion Rate* / *Watch Time*):** Porcentagem média de visualização até o final em vídeos e Reels.
* **Desempenho por Formato & Editoria:** Mapeamento de quais pilares de conteúdo trazem maior engajamento qualificado.

### 2. Saúde da Comunidade (*Community Management*)
* **SLA de Resposta (Tempo Médio de Atendimento):** Agilidade da equipe ao responder DMs e comentários.
* **Análise de Sentimento:** Classificação do tom das interações em Positivo, Neutro e Negativo.
* **Mencionados / UGC (*User Generated Content*):** Volume de postagens espontâneas e marcações da comunidade.

### 3. Engajamento Qualificado
* **Engajamento Ativo vs. Passivo:** Distinção entre interações de alto esforço (comentários, DMs, salvamentos) e baixo esforço (curtidas).
* **Taxa de Engajamento por Alcance Orgânico:** Métricas isoladas do investimento financeiro de mídia.

---

### 🏗️ Arquitetura de Dados & Integração

* **Fontes de Dados:** Arquivos JSON extraídos do **Google Cloud Storage / BigQuery** originados da Graph API da Meta (`facebook_page` e `instagram_pages`).
* **Estrutura Normalizada:** Modelo de dados unificado com identificação de plataforma (`Facebook` / `Instagram`) para garantir escalabilidade.
* **Consumo no Front-end:** Leitura dos dados estruturados via JavaScript e renderização dinâmica na interface HTML.

---

###  Como Abrir e Visualizar o Projeto

### Opção 1: Acesso Online (GitHub Pages)
O projeto está hospedado gratuitamente e pronto para visualização online. Acesse através do link público disponibilizado:
👉 **[Acessar Dashboard Online] https://andressa-sanfe.github.io/dashboard-social/  

### Opção 2: Execução Local
Caso queira rodar o projeto localmente no seu computador:

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
   ```
2. **Navegar até a Pasta:**
   ```bash
   cd NOME-DO-REPOSITORIO
   ```
3. **Executar:**
   Basta dar um duplo clique no arquivo `index.html` ou abri-lo diretamente em qualquer navegador moderno (Chrome, Edge, Firefox, Safari). Nenhuma instalação ou servidor web adicional é necessário!

---

### 🔒Segurança de Dados

Por se tratar de um repositório público no GitHub:
* Confidencialidade: NENHUM dado real, sensível ou confidencial de clientes da agência deve ser enviado ao repositório.
* Mock Data: Utilizei dados fictícios para testes e demonstração do protótipo no GitHub Pages.
