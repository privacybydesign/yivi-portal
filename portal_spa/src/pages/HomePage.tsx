import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";

function HomePage() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <img
          className="dark:invert"
          src="/yivi-logo.svg"
          alt="Yivi logo"
          width={180}
          height={38}
        />
        <h1 className="text-2xl sm:text-4xl font-bold text-center sm:text-left">
          Welcome to the Yivi Portal
        </h1>
        <p className="text-sm sm:text-base text-center sm:text-left">
          Explore the Yivi ecosystem and discover how you can participate.
        </p>

        <div className="grid gap-4 sm:grid-cols-2 w-full max-w-2xl">
          <Card>
            <CardHeader>
              <CardTitle>I want to join Yivi ecosystem</CardTitle>
            </CardHeader>
            <CardContent>
              You can register your organization as a relying party or a
              attestation provider through the Yivi Portal.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/organizations/register">
                    Register Organization
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>The Yivi Ecosystem</CardTitle>
            </CardHeader>
            <CardContent>
              Find out more about the organizations that participate in the Yivi
              ecosystem.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/organizations">View Organizations</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Supported Credentials</CardTitle>
            </CardHeader>
            <CardContent>
              Interested in giving Yivi a try? Search the attribute index of
              Yivi, which catalogues all the supported credentials.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/attribute-index">View Attribute Index</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default HomePage;
