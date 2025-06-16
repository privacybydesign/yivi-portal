import { createContext, useContext } from "react";
import type { RelyingPartyContextValue } from "./RelyingPartyContextType";

export const RelyingPartyContext = createContext<
  RelyingPartyContextValue | undefined
>(undefined);

export const useRelyingParty = () => {
  const context = useContext(RelyingPartyContext);
  if (!context) {
    throw new Error(
      "useRelyingParty must be used within a RelyingPartyContext.Provider"
    );
  }
  return context;
};
