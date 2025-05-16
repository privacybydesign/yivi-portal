// import { Button } from "@/components/ui/button";
// import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
// import { Link } from "react-router-dom";

function PrivacyPolicyPage() {
  return (
    <div className="font-[family-name:var(--font-geist-sans)] max-w-5xl container mx-auto grid p-4 gap-4">
      <h1 className="text-2xl sm:text-4xl font-bold">Privacy</h1>
      <p className="font-bold">
        Jouw privacy vinden wij erg belangrijk. Wij houden ons dan ook aan de
        privacywetgeving. Dit betekent dat je gegevens veilig zijn bij ons en
        dat we er netjes mee omgaan. In deze privacyverklaring leggen we uit wat
        we bij Yivi allemaal doen met informatie die we over jou te weten komen.
        Als je vragen hebt, of wilt weten wat we precies van jou bijhouden, neem
        dan contact met ons op.
      </p>

      <div className="grid gap-8">
        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">
            Yivi Privacyverklaring
          </h3>
          <div>
            <p>
              <strong>Versie 1 november 2024</strong>
            </p>
            <p>
              De Stichting Privacy by Design, Caesar Groep en SIDN Business B.V.
              (hierna: de beheerder) verwerken persoonsgegevens voor het
              realiseren van attribuut-gebaseerde authenticatie en ondertekening
              via het systeem Yivi. De beheerders zijn daarbij verantwoordelijk
              voor de verwerking en vindt jouw privacy erg belangrijk. Zij
              houden zich dan ook aan de privacywetgeving. Dit betekent dat je
              gegevens veilig zijn bij hen en dat zij er netjes mee omgaan.
            </p>
            <p>
              De opzet van Yivi is zodanig dat persoonsgegevens, in de vorm van
              attributen, exclusief bij de gebruiker zelf in de Yivi-app op de
              eigen telefoon of tablet versleuteld worden opgeslagen en dat de
              gebruiker zelf de controle heeft over met wie hij zijn
              persoonsgegevens deelt.
            </p>
            <p>
              Attributen zijn een klein stukje data dat doorgaans een verklaring
              bevat over de eigenaar van het attribuut (bijv. ‘&gt; 18 jaar’).
              Een attribuut is bijvoorbeeld je bankrekeningnummer, naam,
              huisadres, e-mailadres, 06-nummer of Burgerservicenummer (BSN).
              Niemand kan, ook beheerders niet, zien bij welke uitgever van
              attributen de gebruiker attributen ophaalt of met wie de gebruiker
              zijn attributen deelt. Welke attributen door de gebruiker worden
              opgehaald of gedeeld kan eveneens niemand zien. Opgehaalde
              attributen kunnen alleen via de Yivi-app geraadpleegd en gedeeld
              worden. Het hele stelsel is op privacy by design gebaseerd.
            </p>
            <p>
              Het doel van Yivi is om veilig en vertrouwelijk, op basis van
              dataminimalisatie te kunnen inloggen, toegang te kunnen
              verschaffen, toe te stemmen en te ondertekenen bij derde partijen
              die authenticatieprocessen via Yivi uitvoeren.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">
            Wat doen de beheerders met jouw gegevens?
          </h3>
          <div>
            <p>
              Hieronder lees je wat de beheerders doen met de gegevens die zij
              van jou verzamelen via Yivi.
            </p>
            <p>
              Bij de registratie van nieuwe Yivi-gebruikers bewaren de
              beheerders per gebruiker enkel een willekeurig gebruikersnaam (het
              app-ID) en, alleen als de gebruiker deze zelf opgeeft, een
              e-mailadres. Daarnaast slaan ze een zeer beperkte verzameling
              historische gebruiksgegevens op, zoals hieronder nader beschreven
              wordt.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">Grondslag</h3>
          <div>
            <p>
              De wettelijke grondslagen voor de verwerkingen door beheerders als
              verwerkingsverantwoordelijken, in het kader van Yivi, zijn
              toestemming van de betrokkene en noodzakelijk voor het uitvoeren
              van de gebruikersovereenkomst. De verwerking van persoonsgegevens
              door de beheerders is noodzakelijk om de functionaliteiten van
              Yivi en de werking van de app te kunnen waarborgen. Zo is het
              verwerken van het mobiele nummer, het e-mailadres als attribuut,
              het app-ID en de historische gebruiksgegevens noodzakelijk voor de
              verificatie en werking van de app. Daarmee is de verwerking
              noodzakelijk ter uitvoering van de overeenkomst tussen de
              beheerders en de gebruiker van de Yivi-app.
            </p>
            <p>
              Daarnaast geeft de gebruiker, wanneer hij/zij ervoor kiest om van
              de herstelfunctie gebruik te maken, via het doorgeven het
              e-mailadres, expliciet toestemming aan de beheerders om het
              herstel e-mailadres te laten verwerken.
            </p>
            <p>
              De Yivi-app vraagt de gebruiker bij iedere ontvangst en bij iedere
              onthulling van attributen overigens ook expliciet om toestemming
              voor deze actie. Dit vormt de grondslag voor de verwerking van de
              betreffende attributen door deze (derde) partijen.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PrivacyPolicyPage;
