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
  const hasChallenge = hostnames.some((h) => h.dns_challenge);
  if (!hasChallenge) return null;

  return (
    <div className="space-y-4 border border-muted rounded-md p-4 bg-muted/50">
      <h4 className="text-base font-semibold text-muted-foreground">
        DNS Challenges
      </h4>

      <div className="space-y-3">
        {hostnames.map(
          (host, index) =>
            host.dns_challenge && (
              <div
                key={index}
                className="p-4 border rounded-lg bg-white shadow-sm space-y-2"
              >
                <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                  <div>
                    <div className="text-sm font-semibold text-gray-800">
                      {host.hostname}
                    </div>
                    <div className="text-xs text-gray-500">
                      Created at:{" "}
                      {host.dns_challenge_created_at
                        ? new Date(
                            host.dns_challenge_created_at
                          ).toLocaleString()
                        : "N/A"}
                    </div>
                  </div>

                  <div className="mt-2 md:mt-0">
                    {host.dns_challenge_verified ? (
                      <span className="inline-flex items-center gap-1 text-green-700 bg-green-100 border border-green-300 text-xs px-2 py-1 rounded">
                        Verified
                      </span>
                    ) : host.dns_challenge_invalidated_at ? (
                      <span className="inline-flex items-center gap-1 text-red-700 bg-red-100 border border-red-300 text-xs px-2 py-1 rounded">
                        Invalidated
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-yellow-800 bg-yellow-100 border border-yellow-300 text-xs px-2 py-1 rounded">
                        Pending Verification
                      </span>
                    )}

                    {host.manually_verified && (
                      <span className="ml-2 text-xs text-blue-700 bg-blue-100 border border-blue-300 px-2 py-1 rounded">
                        Manually Verified
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-sm">
                  <span className="font-medium">TXT Record:</span>{" "}
                  <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">
                    {host.dns_challenge.replace(/(^\"|\"$)/g, "")}
                  </code>
                </div>

                {host.dns_challenge_verified_at && (
                  <div className="text-xs text-gray-500">
                    Verified at:{" "}
                    {new Date(host.dns_challenge_verified_at).toLocaleString()}
                  </div>
                )}

                {host.dns_challenge_invalidated_at && (
                  <div className="text-xs text-red-500">
                    Invalidated at:{" "}
                    {new Date(
                      host.dns_challenge_invalidated_at
                    ).toLocaleString()}
                  </div>
                )}
              </div>
            )
        )}
      </div>
    </div>
  );
};

export default DnsChallenges;
