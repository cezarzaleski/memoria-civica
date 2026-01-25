'use client'

import React from 'react'
import { Deputado } from '@/lib/types/deputado'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface DeputadoCardProps {
  deputado: Deputado
  onClick?: () => void
}

/**
 * Displays a deputado card with photo, name, party, and state
 */
export function DeputadoCard({ deputado, onClick }: DeputadoCardProps) {
  const initials = deputado.nome
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || '?'

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md active:scale-95',
        'touch-target',
        onClick && 'hover:shadow-lg'
      )}
      onClick={onClick}
    >
      <CardContent className="p-4 sm:p-6">
        <div className="space-y-3">
          {/* Photo or Avatar */}
          <div className="flex justify-center">
            {deputado.foto_url ? (
              <img
                src={deputado.foto_url}
                alt={deputado.nome}
                className="h-32 w-32 rounded-full object-cover border-4 border-primary/10"
              />
            ) : (
              <div
                className={cn(
                  'h-32 w-32 rounded-full flex items-center justify-center',
                  'bg-gradient-to-br from-primary/20 to-primary/10 border-4 border-primary/20',
                  'text-2xl font-bold text-primary'
                )}
              >
                {initials}
              </div>
            )}
          </div>

          {/* Name */}
          <div>
            <h3 className="font-semibold text-center line-clamp-2">
              {deputado.nome}
            </h3>
          </div>

          {/* Party and State */}
          <div className="flex flex-wrap gap-2 justify-center">
            {deputado.partido && (
              <Badge variant="secondary" className="text-xs">
                {deputado.partido}
              </Badge>
            )}
            {deputado.uf && (
              <Badge variant="outline" className="text-xs">
                {deputado.uf}
              </Badge>
            )}
          </div>

          {/* Email if available */}
          {deputado.email && (
            <div className="text-xs text-muted-foreground text-center truncate">
              {deputado.email}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
