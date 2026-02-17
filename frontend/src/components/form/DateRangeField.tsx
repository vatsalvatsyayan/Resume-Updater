import { useFormContext, Controller } from 'react-hook-form';
import { Input, Checkbox } from '@/components/ui';
import { cn } from '@/lib/cn';

export interface DateRangeFieldProps {
  startName: string;
  endName: string;
  presentName: string;
  presentLabel: string;
  startLabel?: string;
  endLabel?: string;
  className?: string;
}

export function DateRangeField({
  startName,
  endName,
  presentName,
  presentLabel,
  startLabel = 'Start Date',
  endLabel = 'End Date',
  className,
}: DateRangeFieldProps) {
  const { control, watch, formState: { errors } } = useFormContext();
  const isPresent = watch(presentName);

  const getNestedError = (name: string) => {
    const parts = name.split('.');
    let current: unknown = errors;
    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = (current as Record<string, unknown>)[part];
      } else {
        return undefined;
      }
    }
    return current as { message?: string } | undefined;
  };

  return (
    <div className={cn('col-span-full', className)}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Controller
          name={startName}
          control={control}
          render={({ field }) => (
            <Input
              type="date"
              label={startLabel}
              {...field}
              value={field.value || ''}
              error={getNestedError(startName)?.message}
            />
          )}
        />
        <div className="space-y-2">
          <Controller
            name={endName}
            control={control}
            render={({ field }) => (
              <Input
                type="date"
                label={endLabel}
                {...field}
                value={field.value || ''}
                disabled={isPresent}
                error={getNestedError(endName)?.message}
                className={cn(isPresent && 'opacity-50')}
              />
            )}
          />
        </div>
      </div>
      <div className="mt-3">
        <Controller
          name={presentName}
          control={control}
          render={({ field }) => (
            <Checkbox
              label={presentLabel}
              checked={field.value}
              onChange={field.onChange}
            />
          )}
        />
      </div>
    </div>
  );
}
