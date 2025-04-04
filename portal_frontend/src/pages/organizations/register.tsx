import { useState } from "react";
import { useRouter } from "next/router";
import { Button } from "@/src/components/ui/button";
import { Input } from "@/src/components/ui/input";
import { axiosInstance } from "@/src/services/axiosInstance";
import Image from 'next/image';


// SET STATES
export default function RegisterOrganization() {
  const [form, setForm] = useState({
    name_en: "",
    name_nl: "",
    slug: "",
    registration_number: "",
    street: "",
    housenumber: "",
    postal_code: "",
    city: "",
    country: "",
    trade_names: [] as string[], // initialize as empty string array
  });
  const [submitting, setSubmitting] = useState(false);
  const [slugEdited, setSlugEdited] = useState(false);
  const [slugError, setSlugError] = useState("");
  const router = useRouter();
  const [tradeNameInput, setTradeNameInput] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);



const generateSlug = (text: string) => {
  return text
    .toLowerCase()
    .replace(/\s+/g, "-")         // replace spaces with hyphen
    .replace(/[^a-z0-9-]/g, "")   // allow only lowercase letters, digits, and hyphen
  
};


  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;

    setForm((prev) => { // form setter function, takes previous state of the form, spreads it to update it
      const updated = { ...prev, [name]: value };

      if (name === "name_en" && !slugEdited) { // if the name of the form field is name_en than update its slug like so
        updated.slug = generateSlug(value);
        setSlugError("");
      }

      return updated; // return updated form inputs
    });

    if (name === "slug") { // if the name of the form field is slug, (user edited the slug instead of using the automatic slug) do a small regex validation check
      setSlugEdited(true);
      const isValid = /^[a-z0-9-]+$/.test(value);
      setSlugError(isValid ? "" : "Slug must be lowercase and only contain letters, numbers, or hyphens.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // prevent default behavior like restarting the page upon form submit
    setSubmitting(true);

    if (!/^[a-z0-9-]+$/.test(form.slug)) { // complain if the slug is invalid
      setSlugError("Slug must be lowercase and only contain letters, numbers, or hyphens.");
      setSubmitting(false);
      return;
    }

    const formData = new FormData();
    formData.append("name_en", form.name_en);
    formData.append("name_nl", form.name_nl);
    formData.append("slug", form.slug);
    formData.append("registration_number", form.registration_number);
    formData.append(
      "contact_address",
      `${form.street} ${form.housenumber}, ${form.postal_code} ${form.city}, ${form.country}`
    );
    formData.append("verified_at", new Date().toISOString());
    formData.append("trade_names", JSON.stringify(form.trade_names));
    if (logoFile) {
      formData.append("logo", logoFile);
    }


    try {
      axiosInstance.post("/v1/organizations/", formData).then((response) => { // axiosInstance helps us send the request with client's access token
        if (response.status === 200) {
        router.push("v1/organizations/"); // for now if the post was successful reroute to organizations main page
      } 
        console.log("response from api", {response})
        
      }).catch((error) => { console.log("error", {error})

      });
    } catch (err) {
      alert(err);
    } finally {
      setSubmitting(false); // ?
    }
  };

  const addTradeName = () => {
  const trimmed = tradeNameInput.trim();
  if (trimmed && !form.trade_names.includes(trimmed)) {
    setForm((prev) => ({
      ...prev,
      trade_names: [...prev.trade_names, trimmed],
    }));
  }
  setTradeNameInput(""); // Clear the input
};

const removeTradeName = (nameToRemove: string) => {
  setForm((prev) => ({
    ...prev,
    trade_names: prev.trade_names.filter((name) => name !== nameToRemove),
  }));
};

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col gap-6 mb-6">
        <h1 className="text-2xl font-bold mb-6">Register Organization</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">English Name</label>
            <Input name="name_en" value={form.name_en} onChange={handleChange} required />
            <small className="text-sm text-gray-500">Formal name of your organization in English.</small>
          </div>
          <div>
            <label className="block mb-1 font-medium">Dutch Name</label>
            <Input name="name_nl" value={form.name_nl} onChange={handleChange} required />
            <small className="text-sm text-gray-500">Formal name of your organization in Dutch.</small>
          </div>

          <div>
            <label className="block mb-1 font-medium">Slug</label>
            <Input name="slug" value={form.slug} onChange={handleChange} required />
            <small className="text-sm text-gray-500">
              Auto-generated from the name. Lowercase, hyphens instead of spaces, no special characters.
            </small>
            {slugError && <p className="text-sm text-red-600 mt-1">{slugError}</p>}
          </div>

          <div>
            <label className="block mb-1 font-medium">Registration Number</label>
            <Input name="registration_number" value={form.registration_number} onChange={handleChange} />
            <small className="text-sm text-gray-500">e.g. KVK number or similar official registration code.</small>
          </div>
          <div>
            <label className="block mb-1 font-medium">Trade Names</label>
            <div className="flex gap-2">
              <Input
                name="trade_name_input"
                value={tradeNameInput}
                onChange={(e) => setTradeNameInput(e.target.value)}
                placeholder="Enter a trade name"
              />
              <Button type="button" onClick={addTradeName}>Add</Button>
            </div>
            {form.trade_names.length > 0 && (
              <ul className="mt-2 space-y-1">
                {form.trade_names.map((name) => (
                  <li key={name} className="flex justify-between items-center bg-gray-100 px-2 py-1 rounded">
                    <span>{name}</span>
                    <button
                      type="button"
                      className="text-red-500 text-sm"
                      onClick={() => removeTradeName(name)}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <small className="text-sm text-gray-500">Click &quot;Add&quot; to insert trade names. You can remove them below.</small>
          </div>
          <fieldset className="border p-4 rounded space-y-2">
            <legend className="font-medium">Contact Address</legend>

            <div>
              <label className="block mb-1 font-medium">Street</label>
              <Input name="street" value={form.street} onChange={handleChange} />
            </div>

            <div>
              <label className="block mb-1 font-medium">House Number</label>
              <Input name="housenumber" value={form.housenumber} onChange={handleChange} />
            </div>

            <div>
              <label className="block mb-1 font-medium">Postal Code</label>
              <Input name="postal_code" value={form.postal_code} onChange={handleChange} />
            </div>

            <div>
              <label className="block mb-1 font-medium">City</label>
              <Input name="city" value={form.city} onChange={handleChange} />
            </div>

            <div>
              <label className="block mb-1 font-medium">Country</label>
              <Input name="country" value={form.country} onChange={handleChange} />
            </div>
          </fieldset>
            <div>
              <label className="block mb-2 font-medium">Organization Logo</label>
              <Input
                type="file"
                accept="image/png, image/jpeg"
                className="file:mr-4 file:py-1 file:px-4 file:rounded file:border-0 file:bg-black file:text-white file:bg-gray-800"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    setLogoFile(e.target.files[0]);
                  }
                }}
              />
              <small className="text-sm text-gray-500">Upload your logo (PNG or JPEG).</small>

              {logoFile && (
                <div className="mt-2">
                  <p className="text-sm text-gray-700">Selected: {logoFile.name}</p>
                  <Image
                    src={URL.createObjectURL(logoFile)}
                    alt="Logo Preview"
                    width={96}
                    height={96}
                    className="mt-2 h-24 rounded border object-contain"
                  />
                  <button
                    type="button"
                    className="text-red-500 text-sm mt-1"
                    onClick={() => setLogoFile(null)}
                  >
                    Remove Image
                  </button>
                </div>
              )}
            </div>

          <Button type="submit" disabled={submitting || !!slugError}>
            {submitting ? "Submitting..." : "Register Organization"}
          </Button>
        </form>
      </div>
    </div>
  );
}
