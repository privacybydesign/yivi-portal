import AppRoutes from "./routes";
import { Toaster } from "sonner";
import { useIdleRefresh } from "@/store";
import "./App.css";

function App() {
  useIdleRefresh();
  return (
    <div>
      <AppRoutes />
      <Toaster richColors />
    </div>
  );
}

export default App;
