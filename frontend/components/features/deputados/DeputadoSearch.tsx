'use client'

import React, { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

interface DeputadoSearchProps {
  onSearch: (query: string) => void
  placeholder?: string
  debounceMs?: number
  disabled?: boolean
  initialValue?: string
}

/**
 * Search input with debounce for filtering deputados
 * Debounces search input by 300ms before triggering callback
 */
export function DeputadoSearch({
  onSearch,
  placeholder = 'Pesquisar deputados...',
  debounceMs = 300,
  disabled = false,
  initialValue = '',
}: DeputadoSearchProps) {
  const [value, setValue] = useState(initialValue)
  const [debouncedValue, setDebouncedValue] = useState(initialValue)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, debounceMs)

    return () => clearTimeout(timer)
  }, [value, debounceMs])

  useEffect(() => {
    onSearch(debouncedValue)
  }, [debouncedValue, onSearch])

  return (
    <div className="w-full">
      <Input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
        className={cn(
          'w-full',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      />
      {debouncedValue && !disabled && (
        <p className="text-xs text-muted-foreground mt-2">
          Buscando por: &ldquo;{debouncedValue}&rdquo;
        </p>
      )}
    </div>
  )
}
