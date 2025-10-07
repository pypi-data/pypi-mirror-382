from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class WhodatBaseModel(BaseModel):
    """Base model for Whodat."""

    model_config = ConfigDict(extra="forbid")


class WhodatRequest(WhodatBaseModel):
    """Request model for Whodat Service."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    whodat_variables: list["WhodatVariables"]
    whodat_modifiers: "WhodatModifiers | None" = None


class WhodatResponse(BaseModel):
    """Response model from Whodat Service."""

    found_personal_ids: list[list[str]]


class WhodatVariables(WhodatBaseModel):
    """All variables available in FREG API.

    Variable documentation is from:
    https://app.swaggerhub.com/apis/skatteetaten/Folkeregisteret_Offentlig_med_hjemmel/1.6.2#/Offentlig%20med%20hjemmel/personsoek
    """

    model_config = ConfigDict(hide_input_in_errors=True)

    ### VARIABLES ###

    # Et eller flere hele ord fra personnavnet, skilt med mellomrom.
    navn: str | None = None

    # 'mann' eller 'kvinne'
    kjoenn: str | None = None

    # Fødselsdato (YYYYMMDD)
    foedselsdato: str | None = None

    # Laveste fødselsår (4 siffer)
    foedselsaarFraOgMed: str | None = None

    # Laveste fødselsår (4 siffer)
    foedselsaarTilOgMed: str | None = None

    # Minst 3 tegn fra begynnelsen av gatenavn
    adressenavn: str | None = None

    # Husnummer, med eller uten bokstav
    husnummer: str | None = None

    # Filtrerer treff på postnummer (4 siffer)
    postnummer: str | None = None

    # Filtrerer treff på kommunenummer (4 siffer)
    kommunenummer: str | None = None

    # Filtrerer treff på fylkesnummer (2 siffer)
    fylkesnummer: str | None = None


class WhodatModifiers(BaseModel):
    """All search modifiers available in FREG API.

    Modifier documentation is from:
    https://app.swaggerhub.com/apis/skatteetaten/Folkeregisteret_Offentlig_med_hjemmel/1.6.2#/Offentlig%20med%20hjemmel/personsoek
    """

    # Treffer oppholdsasdresse i tillegg til bostedsadresse. Default: false
    inkluderOppholdsadresse: bool | None = None

    # Søk også på lignende navn. Default: false
    soekFonetisk: bool | None = None

    # Treffer også døde personer. Default: false
    inkluderDoede: bool | None = None

    # Styrer håndtering av historikk. En av ('gjeldende', 'historisk'). Default: 'gjeldende'.
    # Påvirker kun navn og adresse - for andre opplysninger søkes det alltid kun på gjeldende.
    opplysningsgrunnlag: str | None = None
