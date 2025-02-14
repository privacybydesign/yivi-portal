"use client";

import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const organizations = [
  {
    name: "Gemeente Nijmegen",
    logo: "/logos/nijmegen.jpg",
    domain: "nijmegen.nl",
    issuer: { status: "Active", color: "green" },
    verifier: { status: "Inactive", color: "red" },
  },
  {
    name: "PubHubs",
    domain: "pubhubs.net",
    logo: "/logos/pubhubs.png",
    issuer: { status: "Inactive", color: "red" },
    verifier: { status: "Active", color: "green" },
  },
  {
    name: "Ministerie van Volksgezondheid Welzijn en Sport",
    domain: "orgc.org",
    logo: "/logos/minvws.jpg",
    issuer: { status: "Pending", color: "yellow" },
    verifier: { status: "Active", color: "green" },
  },
];

export default function Organizations() {
  return (
    <div className="container mx-auto px-4 py-10 text-left">
        <h1 className="text-3xl font-bold mb-4">Organizations</h1>
        <Table>
          <TableCaption>Organizations using Yivi.</TableCaption>
          <TableHeader>
            <TableRow>
            <TableHead>Logo</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Domain</TableHead>
              <TableHead>Issuer</TableHead>
              <TableHead>Verifier</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {organizations.map((org, index) => (
              <TableRow key={index}>
                <TableCell>
                  <img src={org.logo} alt={`${org.name} logo`} className="h-10 w-10" />
                </TableCell>
                <TableCell className="font-medium">{org.name}</TableCell>
                <TableCell>{org.domain}</TableCell>
                <TableCell>
                  <Badge className={`text-white`}>
                    {org.issuer.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge className={`text-white`}>
                    {org.verifier.status}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
    </div>
  );
}
