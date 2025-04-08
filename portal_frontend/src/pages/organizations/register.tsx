import { useActionState, useEffect, useState } from 'react';
import { Button } from '@/src/components/ui/button';
import { Input } from '@/src/components/ui/input';
import { Form, FormControl, FormDescription, FormField, FormItem, FormMessage } from '@/src/components/ui/form';
import { Label } from '@/src/components/ui/label';
import { registerOrganization, RegistrationFormState, RegistrationInputs } from '@/src/actions/register-organization';
import { generateSlug } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/src/components/ui/avatar';
import { UploadIcon, XIcon } from 'lucide-react';
import { Control, UseFormSetValue, useFieldArray, useForm, useWatch } from 'react-hook-form';


const defaultFormInput: RegistrationInputs = {
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
  logo: undefined,
};

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
      (Object.entries(formState.errors) as [keyof RegistrationInputs, { message?: string; }][]).forEach(
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
            {/* {logo
              ? 'Logo Preview'
              : <span className="cursor-pointer whitespace-nowrap rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 p-1">Select logo</span>} */}
          </AvatarFallback>
        </Avatar>

        {logo && <button
          type="button"
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
          <form action={register} className="space-y-4">
            <FormField control={form.control} name="logo" render={({ field: { value, onChange, ...field } }) => (
              <FormItem className="grid md:grid-cols-2 items-center md:gap-4">
                <div className="py-1">
                  <Label className="">
                    Organization Logo
                  </Label>
                  <FormDescription>Upload your logo (PNG or JPEG).</FormDescription>
                </div>
                <div className="grid grid-flow-col items-center justify-start gap-4">
                  <LogoPreview {...form} />

                  <Label>
                    <div className="cursor-pointer whitespace-nowrap rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 flex items-center gap-2">
                      <UploadIcon size={12} strokeWidth={3} />
                      Select logo
                    </div>
                    <FormControl>
                      <Input
                        type="file"
                        accept="image/png,image/jpeg"
                        className="hidden"
                        onChange={(event) => onChange(event.target.files?.[0])}
                        {...field}
                      />
                    </FormControl>
                  </Label>
                  {formState.errors.logo &&
                    <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.logo.message}</FormMessage>}
                </div>
              </FormItem>
            )} />

            <FormField control={form.control} name="name_en" render={({ field: { onBlur, ...field } }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>English Name</Label>
                  <FormDescription>
                    Formal name of your organization in English.
                  </FormDescription>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} onBlur={(event) => {
                      if (!form.control.getFieldState('slug').isDirty) {
                        form.setValue('slug', generateSlug(event.target.value.trim()));
                      }

                      onBlur();
                    }} />
                  </FormControl>
                  {formState.errors.name_en &&
                    <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.name_en.message}</FormMessage>}
                </div>
              </FormItem>
            )} />

            <FormField control={form.control} name="name_nl" render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Dutch Name</Label>
                  <FormDescription>
                    Formal name of your organization in Dutch.
                  </FormDescription>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  {formState.errors.name_nl &&
                    <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.name_nl.message}</FormMessage>}
                </div>
              </FormItem>
            )} />

            <FormField control={form.control} name="slug" render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Slug</Label>
                  <FormDescription>
                    Auto-generated from the name. Lowercase, hyphens instead of spaces, no special characters.
                  </FormDescription>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} pattern='[a-z0-9\-]+' />
                  </FormControl>
                  {formState.errors.slug &&
                    <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.slug.message}</FormMessage>}
                </div>
              </FormItem>
            )} />

            <FormField control={form.control} name="registration_number" render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Registration Number</Label>
                  <FormDescription>
                    e.g. KVK number or similar official registration code.
                  </FormDescription>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  {formState.errors.registration_number &&
                    <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.registration_number.message}</FormMessage>}
                </div>
              </FormItem>
            )} />

            <FormField control={form.control} name="trade_names" render={() => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Trade Names</Label>
                  <FormDescription>
                    Click &quot;Add&quot; to insert trade names. You can remove them below.
                  </FormDescription>
                </div>
                <div className="flex gap-2">
                  <FormControl>
                    <Input placeholder="Enter a trade name" value={tradeNameInput} onChange={(event) => setTradeNameInput(event.target.value)} />
                  </FormControl>
                  <Button type="button" onClick={addTradeName}>
                    Add
                  </Button>
                  {formState.errors.trade_names &&
                    <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.trade_names.message}</FormMessage>}
                </div>
              </FormItem>
            )} />

            {tradeNames.fields.map((item, index) => (
              <FormField key={item.id} control={form.control} name={`trade_names.${index}`} render={({ field }) => (
                <div className="md:w-1/2 md:pl-2 md:ml-auto flex gap-2 relative">
                  <FormControl>
                    <Input className="pr-10" {...field} />
                  </FormControl>
                  <Button type="button" className="absolute inset-y-1.5 right-1.5 !h-auto my-auto !p-1" onClick={() => tradeNames.remove(index)}>
                    <XIcon />
                  </Button>
                </div>
              )} />
            ))}

            <fieldset className="border border-primary-light rounded-lg p-4">
              <legend className="font-medium">Contact Address</legend>

              <FormField control={form.control} name="street" render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>Street</Label>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>

                    {formState.errors.registration_number &&
                      <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.registration_number.message}</FormMessage>}
                  </div>
                </FormItem>
              )} />

              <FormField control={form.control} name="housenumber" render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>House Number</Label>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>

                    {formState.errors.registration_number &&
                      <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.registration_number.message}</FormMessage>}
                  </div>
                </FormItem>
              )} />

              <FormField control={form.control} name="postal_code" render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>Postal Code</Label>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>

                    {formState.errors.registration_number &&
                      <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.registration_number.message}</FormMessage>}
                  </div>
                </FormItem>
              )} />

              <FormField control={form.control} name="city" render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>City</Label>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>

                    {formState.errors.registration_number &&
                      <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.registration_number.message}</FormMessage>}
                  </div>
                </FormItem>
              )} />

              <FormField control={form.control} name="country" render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>Country</Label>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>

                    {formState.errors.registration_number &&
                      <FormMessage className="text-sm text-red-600 mt-1">{!formState.errors.registration_number.message}</FormMessage>}
                  </div>
                </FormItem>
              )} />
            </fieldset>

            <Button type="submit" disabled={pending} className="col-span-2">
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
