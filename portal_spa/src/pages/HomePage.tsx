import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";

function HomePage() {
  return (
    <div className="flex justify-center items-start p-6">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start w-full max-w-3xl">
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

        <div className="grid gap-4 sm:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Join the Yivi ecosystem</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-between flex-1">
              You can register your organization as a relying party or a
              attestation provider through the Yivi Portal.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/organizations/register">
                    Register an organization
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Already a part of Yivi?</CardTitle>
            </CardHeader>
            <CardContent className=" flex-col flex-1">
              <span>
                Send an email to{" "}
                <a
                  className="text-blue-600 hover:underline"
                  href="mailto:support@yivi.app"
                >
                  support@yivi.app
                </a>{" "}
                with the name of your organization and the email(s) and we will
                get back to you as soon as possible.
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>The Yivi ecosystem</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-between flex-1">
              Find out more about the organizations that participate in the Yivi
              ecosystem.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/organizations">View organizations</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Supported credentials</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-between flex-1">
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
