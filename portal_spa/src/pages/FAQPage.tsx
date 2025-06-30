import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom"; // For React Router (Vite apps)

export default function FAQPage() {
  const location = useLocation(); // From react-router-dom
  const [open, setOpen] = useState<string>("");

  useEffect(() => {
    // Listen to changes in the location (hash)
    if (location.hash) {
      setOpen(location.hash.replace("#", ""));
    }
  }, [location]);
  // ...

  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Frequently Asked Questions
      </h1>
      <Accordion
        type="single"
        collapsible
        className="w-full space-y-2"
        value={open}
        onValueChange={setOpen}
      >
        <AccordionItem value="what-is-yivi">
          <AccordionTrigger className="text-lg font-medium">
            What is Yivi Portal?
          </AccordionTrigger>
          <AccordionContent className="text-gray-700">
            Yivi Portal is a platform that makes it easy for organizations to
            become part of Yivi. The portal aims to simplify the process of
            onboarding organizations as relying parties or attestation
            providers.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="why-register-relying-party">
          <AccordionTrigger className="text-lg font-medium">
            Why should I register as a relying party?
          </AccordionTrigger>
          <AccordionContent className="text-gray-700">
            Yivi is free open-source software which enables relying parties to
            request data from their users in a privacy-friendly way. Registering
            as a relying party means that you officially become a part of the
            Yivi ecosystem. This allows your users to see a name and logo
            associated with your organization when they are asked to share their
            data. If this is not the case, the users will see only your hostname
            and the Yivi app warns them that they are sharing their data with a
            party not registered with Yivi so they can make an informed decision
            about sharing their data.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="why-verify-hostname">
          <AccordionTrigger className="text-lg font-medium">
            Why do I have to verify my hostname?
          </AccordionTrigger>
          <AccordionContent className="text-gray-700">
            Verifying your hostname ensures that you are the legitimate owner of
            the domain you are registering.
          </AccordionContent>
          <AccordionItem value="why-select-attributes-for-relying-party">
            <AccordionTrigger className="text-lg font-medium">
              Why does my relying party need to disclose which attributes are
              being requested?
            </AccordionTrigger>
            <AccordionContent className="text-gray-700">
              This helps us keep track of which attributes are used per relying
              party, and how sensitive these attributes are. For example, if a
              relying party needs to ask for a user's BSN (Burgerservicenummer),
              it is important to for what purpose is this needed for and if the
              use is justified. This is to prevent oversharing of sensitive data
              and to keep our users' data private and shared only when
              necessary.
            </AccordionContent>
          </AccordionItem>
        </AccordionItem>
        <AccordionItem value="why-context-description">
          <AccordionTrigger className="text-lg font-medium">
            Why does my relying party needs to have a context?
          </AccordionTrigger>
          <AccordionContent className="text-gray-700">
            The context description is a short description on why you need the
            combination of attributes you are requesting. For example you need
            have an alchohol web shop and you ask the user for their age range,
            as well as an email address to send them a receipt.
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
