import AppRoutes from "./routes";
import { Toaster } from "sonner";
import { useAuthInit } from "@/store";

function App() {
  useAuthInit();
  return (
    <div>
      <AppRoutes />
      <Toaster richColors />
    </div>
  );
}

export default App;
