import { useState } from "react";
import { useRouter } from "next/router";
import { Button } from "@/src/components/ui/button";
import { Input } from "@/src/components/ui/input";
import { Textarea } from "@/src/components/ui/textarea";
import { axiosInstance } from "@/src/services/axiosInstance";

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
    trade_names: "{}",
  });

  const [submitting, setSubmitting] = useState(false);
  const [slugEdited, setSlugEdited] = useState(false);
  const [slugError, setSlugError] = useState("");
  const router = useRouter();

  const generateSlug = (text: string) => {
    return text
      .toLowerCase()
      .replace(/\s+/g, "_")
      .replace(/[^a-z0-9_]/g, "");
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;

    setForm((prev) => {
      const updated = { ...prev, [name]: value };

      if (name === "name_en" && !slugEdited) {
        updated.slug = generateSlug(value);
        setSlugError("");
      }

      return updated;
    });

    if (name === "slug") {
      setSlugEdited(true);
      const isValid = /^[a-z0-9_]+$/.test(value);
      setSlugError(isValid ? "" : "Slug must be lowercase and only contain letters, numbers, or underscores.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    if (!/^[a-z0-9_]+$/.test(form.slug)) {
      setSlugError("Slug must be lowercase and only contain letters, numbers, or underscores.");
      setSubmitting(false);
      return;
    }

    const payload = {
      name_en: form.name_en,
      name_nl: form.name_nl,
      slug: form.slug,
      registration_number: form.registration_number,
      contact_address: {
        street: form.street,
        housenumber: form.housenumber,
        postal_code: form.postal_code,
        city: form.city,
        country: form.country,
      },
      verified_at: new Date().toISOString(),
      trade_names: JSON.parse(form.trade_names || "{}"),
    };

    try {
      axiosInstance.post("/v1/organizations", payload).then((response) => {
        
      }).catch((error) => {

      });


      const res = await fetch("/api/organizations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        router.push("/organizations");
      } else {
        const error = await res.json();
        alert("Failed to register: " + (error.message || res.status));
      }
    } catch (err) {
      alert("Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col gap-6 mb-6">
        <h1 className="text-2xl font-bold mb-6">Register Organization</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Name</label>
            <Input name="name_en" value={form.name_en} onChange={handleChange} required />
            <small className="text-sm text-gray-500">Formal name of your organization in English.</small>
          </div>

          <div>
            <label className="block mb-1 font-medium">Slug</label>
            <Input name="slug" value={form.slug} onChange={handleChange} required />
            <small className="text-sm text-gray-500">
              Auto-generated from the name. Lowercase, underscores instead of spaces, no special characters.
            </small>
            {slugError && <p className="text-sm text-red-600 mt-1">{slugError}</p>}
          </div>

          <div>
            <label className="block mb-1 font-medium">Registration Number</label>
            <Input name="registration_number" value={form.registration_number} onChange={handleChange} />
            <small className="text-sm text-gray-500">e.g. KVK number or similar official registration code.</small>
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

          <Button type="submit" disabled={submitting || !!slugError}>
            {submitting ? "Submitting..." : "Register Organization"}
          </Button>
        </form>
      </div>
    </div>
  );
}
