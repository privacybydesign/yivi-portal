import React from "react";

interface Hostname {
  hostname: string;
  dns_challenge?: string;
  dns_challenge_created_at?: string;
  dns_challenge_verified?: boolean;
  dns_challenge_verified_at?: string;
  dns_challenge_invalidated_at?: string;
  manually_verified?: boolean;
}

interface DnsChallengesProps {
  hostnames: Hostname[];
}

const DnsChallenges: React.FC<DnsChallengesProps> = ({ hostnames }) => {
  const hasData = hostnames.some((h) => h.dns_challenge || h.manually_verified);

  if (!hasData) return null;

  return (
    <div className="space-y-4 border border-muted rounded-md p-4 bg-muted/50">
      <h4 className="text-base font-semibold ">DNS challenges</h4>
      <p className="text-sm text-muted-foreground">
        To make sure that the entered domains belongs to this organization,
        please add the provided TXT record to your DNS settings.
        <br />
        This record must remain in place for as long as you intend to use the
        domain with Yivi. If the challenge record is removed after verification,
        the domain will no longer be considered verified.
      </p>

      {/* Conditionally render DNS verification state  */}
      <div className="space-y-3">
        {hostnames.map(
          (host, index) =>
            (host.dns_challenge || host.manually_verified) && (
              <div
                key={index}
                className="p-4 border rounded-lg bg-white shadow-sm space-y-2"
              >
                <div className="flex-col md:flex-row md:justify-between md:items-start gap-4">
                  <div className="text-sm font-semibold text-gray-800">
                    {host.hostname}

                    {host.dns_challenge_created_at && (
                      <div className="text-xs text-gray-500">
                        Created at:{" "}
                        {new Date(
                          host.dns_challenge_created_at
                        ).toLocaleString()}
                      </div>
                    )}
                  </div>

                  {/* Tags */}
                  <div className="gap-2">
                    <div className="flex gap-2 justify-end">
                      {host.manually_verified && (
                        <span className="inline-flex items-center gap-1 text-blue-700 bg-blue-100 border border-blue-300 text-xs px-2 py-1 rounded">
                          Manually Verified
                        </span>
                      )}

                      {host.dns_challenge_verified && (
                        <span className="inline-flex items-center gap-1 text-green-700 bg-green-100 border border-green-300 text-xs px-2 py-1 rounded">
                          Verified
                        </span>
                      )}

                      {host.dns_challenge_invalidated_at && (
                        <span className="inline-flex items-center gap-1 text-red-700 bg-red-100 border border-red-300 text-xs px-2 py-1 rounded">
                          Invalidated
                        </span>
                      )}

                      {host.dns_challenge && !host.dns_challenge_verified && (
                        <span className="inline-flex items-center gap-1 text-yellow-800 bg-yellow-100 border border-yellow-300 text-xs px-2 py-1 rounded">
                          Pending verification
                        </span>
                      )}
                    </div>

                    {host.dns_challenge && (
                      <div className="flex flex-col gap-1">
                        <div className="text-sm font-medium mb-1">
                          TXT record
                        </div>
                        <code className="block bg-gray-100 px-2 py-3 rounded text-s break-all">
                          {host.dns_challenge.replace(/(^"|"$)/g, "")}
                        </code>
                        {host.dns_challenge_verified_at && (
                          <div className="text-xs text-gray-500 mt-1">
                            Verified at:{" "}
                            {new Date(
                              host.dns_challenge_verified_at
                            ).toLocaleString()}
                          </div>
                        )}
                      </div>
                    )}

                    {host.dns_challenge_invalidated_at && (
                      <div className="text-xs text-red-500 mt-1">
                        Invalidated at:{" "}
                        {new Date(
                          host.dns_challenge_invalidated_at
                        ).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
        )}
      </div>
    </div>
  );
};

export default DnsChallenges;
