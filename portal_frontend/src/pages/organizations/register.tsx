import { useActionState, useEffect, useState } from 'react';
import { Button } from '@/src/components/ui/button';
import { Input } from '@/src/components/ui/input';
import { generateSlug } from '@/lib/utils';
import { registerOrganization} from '@/src/actions/register-organization';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/src/components/ui/form';
import { Control, UseFormSetValue, useFieldArray, useForm, useWatch, FieldErrors } from 'react-hook-form';
import { Avatar, AvatarFallback, AvatarImage } from '@/src/components/ui/avatar';
import { XIcon } from 'lucide-react';


export type RegistrationInputs = {
  name_en: string;
  name_nl: string;
  slug: string;
  registration_number: string;
  street: string;
  housenumber: string;
  postal_code: string;
  city: string;
  country: string;
  trade_names: string[];
  logo: File | undefined;
};

export type RegistrationFormState = {
  values: RegistrationInputs;
  errors: Partial<FieldErrors<RegistrationInputs>>;
  globalError?: string;
  success?: boolean;
  redirectTo?: string;
};

const defaultFormInput:RegistrationInputs = {
        name_en: '',
        name_nl: '',
        slug: '',
        registration_number: '',
        street: '',
        housenumber: '',
        postal_code: '',
        city: '',
        country: '',
        trade_names: [],
        logo: undefined,}

export default function RegisterOrganization() {
  const [formState, register, pending] = useActionState<RegistrationFormState, FormData>(
    registerOrganization,
    {
      values: defaultFormInput,
      errors: {}
    }
  );

  const form = useForm<RegistrationInputs>({
    defaultValues: formState?.values ?? defaultFormInput,
  });

useEffect(() => {
    form.clearErrors();

  if (formState?.errors) {
    (Object.entries(formState.errors) as [keyof RegistrationInputs, { message?: string }][]).forEach(
      ([field, error]) => {
        if (error?.message) {
          form.setError(field, {
            type: 'server',
            message: error?.message,
          });
        }
      }
    );
  }
}, [formState?.errors, form]);


  const tradeNames = useFieldArray<RegistrationInputs>({
    control: form.control,
    name: 'trade_names' as never
  });

  const [tradeNameInput, setTradeNameInput] = useState('');

  const LogoPreview = ({ control, setValue }: { control: Control<RegistrationInputs>; setValue: UseFormSetValue<RegistrationInputs>; }) => {
    const logo = useWatch({ control, name: "logo" });

    return (
      <div className="relative size-24">
        <Avatar className="!size-24">
          <AvatarImage src={logo ? URL.createObjectURL(logo) : ''}
            className="rounded-full border object-contain" />
          <AvatarFallback>
            {logo
              ? 'Logo Preview'
              : <span className="cursor-pointer whitespace-nowrap rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 p-1">Select logo</span>}
          </AvatarFallback>
        </Avatar>

        {logo && <button
          type="button"
          aria-description="Remove logo"
          onClick={() => setValue('logo', undefined)}
          className="bg-red-400 rounded-full p-1 absolute top-0 right-0"
        >
          <XIcon size={12} strokeWidth={3} />
        </button>}
      </div>
    );
  };

  const addTradeName = (): void => {
    const trimmed = tradeNameInput.trim();

    if (trimmed) {
      tradeNames.append(trimmed);
    }

    // Clear the input
    setTradeNameInput('');
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col gap-6 mb-6">
        <h1 className="text-2xl font-bold mb-6">Register Organization</h1>
        <Form {...form}>
          <form action={register} className="md:grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <FormField control={form.control} name="name_en" render={({ field: { onBlur, ...field } }) => (
                <FormItem>
                  <FormLabel>English Name</FormLabel>
                  <FormControl>
                    <Input {...field} onBlur={(event) => {
                      if (!form.control.getFieldState('slug').isDirty) {
                        form.setValue('slug', generateSlug(event.target.value.trim()));
                      }

                      onBlur();
                    }} />
                  </FormControl>
                  <FormDescription>
                    Formal name of your organization in English.
                  </FormDescription>
                    <FormMessage  />
                </FormItem>
              )} />

              <FormField control={form.control} name="name_nl" render={({ field }) => (
                <FormItem>
                  <FormLabel>Dutch Name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormDescription>
                    Formal name of your organization in Dutch.
                  </FormDescription>
                    <FormMessage />
                </FormItem>
              )} />

              <FormField control={form.control} name="slug" render={({ field }) => (
                <FormItem>
                  <FormLabel>Slug</FormLabel>
                  <FormControl>
                    <Input {...field} pattern='[a-z0-9\-]+' />
                  </FormControl>
                  <FormDescription>
                    Auto-generated from the name. Lowercase, hyphens instead of spaces, no special characters.
                  </FormDescription>
                    <FormMessage />
                </FormItem>
              )} />

              <FormField control={form.control} name="registration_number" render={({ field }) => (
                <FormItem>
                  <FormLabel>Registration Number</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormDescription>
                    e.g. KVK number or similar official registration code.
                  </FormDescription>
                    <FormMessage />
                </FormItem>
              )} />

              <FormField control={form.control} name="trade_names" render={() => (
                <FormItem>
                  <FormLabel>Trade Names</FormLabel>
                  <div className="flex gap-2">
                    <FormControl>
                      <Input placeholder="Enter a trade name" value={tradeNameInput} onChange={(event) => setTradeNameInput(event.target.value)} />
                    </FormControl>
                    <Button type="button" onClick={addTradeName}>
                      Add
                    </Button>
                  </div>
                  <FormDescription>
                    Click &quot;Add&quot; to insert trade names. You can remove them below.
                  </FormDescription>
                    <FormMessage />
                </FormItem>
              )} />

              {tradeNames.fields.map((item, index) => (
                <FormField key={item.id} control={form.control} name={`trade_names.${index}`} render={({ field }) => (
                  <div className="flex gap-2 relative">
                    <FormControl>
                      <Input className="pr-10" {...field} />
                    </FormControl>
                    <Button type="button" className="absolute inset-y-1.5 right-1.5 !h-auto my-auto !p-1" onClick={() => tradeNames.remove(index)}>
                      <XIcon />
                    </Button>
                  </div>
                )} />
              ))}

              <FormField control={form.control} name="logo" render={({ field: { onChange } }) => (
                <FormItem className="flex items-center gap-2">
                  <div className="grow">
                    <FormLabel>Organization Logo
                      <LogoPreview {...form} />
                      <FormControl>
                        <Input
                          type="file"
                          accept="image/png,image/jpeg"
                          className="hidden"
                          onChange={(event) => onChange(event.target.files?.[0])}
                        />
                      </FormControl>
                    </FormLabel>
                    <FormDescription>Upload your logo (PNG or JPEG).</FormDescription>
                      <FormMessage />
                  </div>
                </FormItem>
              )} />
            </div>

            <fieldset className="border p-4 rounded space-y-2 mb-auto">
              <legend className="font-medium">Contact Address</legend>

              <FormField control={form.control} name="street" render={({ field }) => (
                <FormItem>
                  <FormLabel>Street</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                </FormItem>
              )} />

              <FormField control={form.control} name="housenumber" render={({ field }) => (
                <FormItem>
                  <FormLabel>House Number</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                </FormItem>
              )} />

              <FormField control={form.control} name="postal_code" render={({ field }) => (
                <FormItem>
                  <FormLabel>Postal Code</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                </FormItem>
              )} />

              <FormField control={form.control} name="city" render={({ field }) => (
                <FormItem>
                  <FormLabel>City</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                </FormItem>
              )} />

              <FormField control={form.control} name="country" render={({ field }) => (
                <FormItem>
                  <FormLabel>Country</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                </FormItem>
              )} />
            </fieldset>

            <Button type="submit" disabled={pending}>
              {pending ? 'Submitting...' : 'Register Organization'}
            </Button>
            {formState?.globalError && (
            <div className="col-span-2 text-sm text-red-600 font-medium">
              {formState.globalError}
            </div>
          )}

          </form>
        </Form>
      </div>
    </div>
  );
}
