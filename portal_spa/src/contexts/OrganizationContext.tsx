import { createContext, useContext } from "react";

export const OrganizationContext = createContext<Record<string, string>>({});
export const useOrganizationNames = () => useContext(OrganizationContext);
