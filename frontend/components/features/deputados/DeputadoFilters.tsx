'use client'

import React from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface DeputadoFiltersProps {
  onFilterChange: (filters: { partido?: string; uf?: string }) => void
  disabled?: boolean
  selectedPartido?: string
  selectedUf?: string
}

// Common Brazilian political parties
const PARTIDOS = [
  'PT',
  'PSD',
  'MDB',
  'PP',
  'PL',
  'PSB',
  'PSOL',
  'PCdoB',
  'PDT',
  'PRD',
  'MV',
  'Republicanos',
  'PRP',
  'Solidariedade',
  'Podemos',
  'PV',
  'PROS',
  'Avante',
  'PMN',
  'Patriota',
  'REDE',
  'PMB',
  'PSC',
  'PTB',
  'PSTU',
  'PCO',
]

// Brazilian states
const UFS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
]

/**
 * Filter controls for partido and UF
 */
export function DeputadoFilters({
  onFilterChange,
  disabled = false,
  selectedPartido,
  selectedUf,
}: DeputadoFiltersProps) {
  const handlePartidoChange = (value: string) => {
    onFilterChange({
      partido: value || undefined,
      uf: selectedUf,
    })
  }

  const handleUfChange = (value: string) => {
    onFilterChange({
      partido: selectedPartido,
      uf: value || undefined,
    })
  }

  const handleClear = () => {
    onFilterChange({})
  }

  const hasActiveFilters = selectedPartido || selectedUf

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Filtros</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="partido-select" className="text-sm font-medium">
            Partido
          </label>
          <Select
            value={selectedPartido || ''}
            onValueChange={handlePartidoChange}
            disabled={disabled}
          >
            <SelectTrigger id="partido-select" className="w-full h-10">
              <SelectValue placeholder="Selecione um partido" />
            </SelectTrigger>
            <SelectContent>
              {PARTIDOS.map((partido) => (
                <SelectItem key={partido} value={partido}>
                  {partido}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label htmlFor="uf-select" className="text-sm font-medium">
            Estado (UF)
          </label>
          <Select
            value={selectedUf || ''}
            onValueChange={handleUfChange}
            disabled={disabled}
          >
            <SelectTrigger id="uf-select" className="w-full h-10">
              <SelectValue placeholder="Selecione um estado" />
            </SelectTrigger>
            <SelectContent>
              {UFS.map((uf) => (
                <SelectItem key={uf} value={uf}>
                  {uf}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {hasActiveFilters && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleClear}
            disabled={disabled}
            className="w-full"
          >
            Limpar Filtros
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
