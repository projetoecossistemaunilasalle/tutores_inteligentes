# HubSmartTutor — Central de Contas Desktop do STI

O HubSmartTutor tem como objetivo apoiar a governança do Sistema de Tutores Inteligentes (STI). A Central de Contas Desktop é concebida para uso administrativo e acadêmico: gerencia identidades, estrutura de cursos, configurações dos tutores de IA e indicadores institucionais.

Esta documentação consolida os requisitos descritos em `Documentacao_Normalizacao_STI_Desktop.md.pdf`. Ela descreve o produto desejado; não significa que todos os recursos já estejam implementados neste repositório.

## Estado atual do repositório

O projeto versionado é um projeto C++ de uma fork especializada em desenvolvimento de software da Unreal Engine 5.7, com o módulo `ApplicationDefault`, conteúdo em Blueprints e configuração para Windows. Há classes-base para Game Instance, subsistemas, configurações e utilitários, além de assets de exemplo para lógica comum e Remote Control.

O código e os assets disponíveis servem como ponto de partida. A integração com o STI, autenticação institucional, gestão administrativa, banco de dados e relatórios descritos abaixo ainda precisa ser implementada e validada. O documento de requisitos prevê um cliente desktop conectado a um backend Django; essa arquitetura deve ser conciliada com a base atual em Unreal Engine antes de iniciar a integração.

## Escopo funcional previsto

### Identidade e acesso

- Autenticar operadores com SSO institucional por OIDC/OAuth 2.0, usando o navegador padrão e um provedor institucional, como Microsoft Entra ID.
- Aplicar controle de acesso baseado em papéis (RBAC) para Administradores, Professores e Alunos.
- Permitir que administradores criem, atualizem, suspendam e excluam logicamente contas.
- Vincular contas de estudantes ao perfil de aprendizagem `PerfilAluno`, necessário ao acompanhamento de proficiência.
- Permitir cadastro e importação em lote de usuários por CSV ou Excel, com validação de dados e papéis.

### Gestão acadêmica

- Organizar semestres, turmas, disciplinas e lições.
- Associar professores titulares às disciplinas e matricular alunos nas turmas.
- Manter a estrutura acadêmica alinhada com a utilizada pelo webapp dos tutores.
- Incluir disciplinas de programação como C e Python, conforme o documento de requisitos.

### Governança de IA

- Exibir o estado operacional do motor de IA.
- Permitir a configuração administrativa de limites de tokens para a API Groq.
- Consultar o estado do ChromaDB e acionar rotinas de indexação de materiais didáticos.
- Registrar alterações de parâmetros e ações de indexação para auditoria.

### Indicadores e relatórios

- Consolidar indicadores de engajamento, tentativas de quiz, tópicos com dificuldade e possíveis sinais de evasão.
- Disponibilizar uma visão executiva para gestores acadêmicos.
- Gerar relatórios filtrados por período e contexto acadêmico, com pré-visualização e exportação em PDF e CSV/Excel.
- Conferir os dados exportados com as informações consolidadas no sistema.

## Telas previstas

1. **Login institucional:** inicia o fluxo de autenticação SSO no navegador.
2. **Dashboard executivo:** apresenta uso global, engajamento, desempenho e alertas acadêmicos.
3. **Gestão de contas:** lista, filtra e administra usuários, status e papéis; oferece importação em lote.
4. **Gestão acadêmica:** organiza semestres, disciplinas, professores e alunos por turma.
5. **Configuração de bots e IA:** monitora serviços e administra parâmetros e indexação.
6. **Relatórios:** permite selecionar filtros, visualizar resultados e exportar dados.

## Requisitos não funcionais e segurança

- Não armazenar nem manipular senhas institucionais no aplicativo. A autenticação deve ser delegada ao fluxo SSO.
- Validar os papéis e as permissões no backend; ocultar opções na interface não substitui autorização no servidor.
- Integrar-se ao backend Django por ORM ou, preferencialmente para um cliente separado, por endpoints administrativos protegidos.
- Prever SQLite para desenvolvimento e PostgreSQL para produção, conforme a configuração definida para o ambiente do STI.
- Usar conexões seguras e registrar ações administrativas, incluindo alterações de contas, turmas e parâmetros.
- Tratar operações em lote de forma íntegra e informar erros de validação ou comunicação sem indicar sucesso quando a operação falhar.

## Critérios de conclusão

Uma funcionalidade deve ser considerada pronta quando:

- estiver revisada, testada e integrada ao backend do STI;
- autenticação SSO e autorização RBAC forem validadas para cada papel;
- operações de cadastro e alteração persistirem os dados corretamente;
- relatórios e exportações corresponderem aos dados consolidados;
- a interface e a comunicação forem verificadas em ambiente de desenvolvimento institucional.

## Executar o projeto atual

1. Instale uma versão compatível do Unreal Engine **5.7** e a toolchain C++ necessária para projetos Unreal.
2. Abra `HubSmartTutor.uproject` no Unreal Editor.
3. Se solicitado, gere os arquivos de projeto e compile o módulo `ApplicationDefault`.
4. Execute o projeto pelo editor e abra o mapa principal disponível em `Content/Map`.

O fluxo acima inicia a base Unreal atual; ele não configura nem valida os serviços SSO, Django, Groq ou ChromaDB descritos nos requisitos.

## Estrutura principal

```text
Config/                         Configurações do projeto Unreal
Content/                        Mapas, Blueprints e assets
  Folder_CommomLogic/           Blueprints e elementos de lógica comum
  Map/                           instancia de execução
  RemoteControlFolder/           Assets de Remote Control
Source/ApplicationDefault/      Código C++ do módulo principal
HubSmartTutor.uproject           Definição do projeto Unreal
```

## Documento de referência

Os requisitos de produto foram extraídos de `Documentacao_Normalizacao_STI_Desktop.md.pdf` (Documento de Normalização e Requisitos — Central de Contas Desktop do STI). O PDF original não está incluído neste repositório.
