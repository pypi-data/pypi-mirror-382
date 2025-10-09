from enum import Enum


class EFaseRetificacao(Enum):
    NaoIniciado = 0
    SolicitacaoXml = 1
    AguardandoXml = 2
    DownloadXml = 3
    ExtraindoDadosDoXml = 4
    AguardandoRubrica = 5
    EstruturandoXmlAberturaCompetencia = 6
    EstruturandoXmlInclusaoRubricas = 7
    EstruturandoXmlExclusaoPagamentos = 8
    EstruturandoXmlRetificacaoRemuneracao = 9
    EstruturandoXmlInclusaoPagamentos = 10
    EstruturandoXmlDesligamento = 11
    EstruturandoXmlFechamentoCompetencia = 12
    AberturaDeCompetencia = 13
    ConsultandoESocialAberturaCompetencia = 14
    InclusaoDasRubricas = 15
    ConsultandoESocialInclusaoRubricas = 16
    ExclusaoDePagamentos = 17
    ConsultandoESocialExclusaoPagamentos = 18
    RetificacaoDaRemuneracao = 19
    ConsultandoESocialRetificacaoRemuneracao = 20
    InclusaoDosPagamentos = 21
    ConsultandoESocialInclusaoPagamentos = 22
    Desligamento = 23
    ConsultandoESocialDesligamento = 24
    FechamentoDeCompetencia = 25
    ConsultandoESocialFechamentoCompetencia = 26
    Finalizado = 27
