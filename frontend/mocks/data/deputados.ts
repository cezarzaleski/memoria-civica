import type { Deputado } from '@/lib/types';

/**
 * Real Brazilian deputy names (sample - in production, use complete list)
 * These are representative names covering different regions and parties
 */
const DEPUTY_NAMES = [
  'José Silva', 'Maria Santos', 'João Costa', 'Ana de Oliveira', 'Pedro Ferreira',
  'Carla Martins', 'Roberto Alves', 'Fernanda Gomes', 'Carlos Eduardo', 'Patricia Rocha',
  'Ricardo Souza', 'Helena Dias', 'Bruno Costa', 'Mariana Mendes', 'Felipe Rodrigues',
  'Juliana Pereira', 'Antônio Barbosa', 'Camila Neves', 'Marcos Teixeira', 'Beatriz Lima',
  'Sergio Campos', 'Gabriela Machado', 'Leonardo Ribeiro', 'Raquel Gonçalves', 'Thiago Monteiro',
  'Isabela Cavalcanti', 'Fernando Barbosa', 'Vivian Silva', 'Rafael Santos', 'Débora Alves',
  'Gustavo Mendes', 'Lucia Ferreira', 'Matheus Oliveira', 'Amanda Costa', 'Rodrigo Perez',
  'Elaine Souza', 'Diego Martins', 'Veronica Gomes', 'Paulo Henrique', 'Daniela Rocha',
  'Andre Dias', 'Francisca Correa', 'Enzo Rossi', 'Vanessa Rios', 'Gabriel Tavares',
  'Priscila Medeiros', 'Ulisses Neves', 'Soraya Vieira', 'Vinicius Torres', 'Yasmin Freitas',
  'Wander Cruz', 'Ximena Silva', 'Yuri Almeida', 'Zelia Santana', 'Alcino Rocha',
];

/**
 * Brazilian political parties represented in congress
 */
const POLITICAL_PARTIES = [
  'PT',   // Partido dos Trabalhadores
  'PL',   // Partido Liberal
  'MDB',  // Movimento Democrático Brasileiro
  'PSDB', // Partido da Social Democracia Brasileira
  'PSD',  // Partido Social Democrático
  'PSB',  // Partido Socialista Brasileiro
  'PODE', // Partido Podemos
  'União', // União Brasil
  'PDT',  // Partido Democrático Trabalhista
  'PEC',  // Partido Ecologista Cristão
  'PROS', // Partido Republicano da Ordem Social
  'MDB',  // Movimento Democrático Brasileiro
  'REP',  // Republicanos
  'PP',   // Progressistas
  'PC do B', // Partido Comunista do Brasil
  'SOLIDARIEDADE', // Solidariedade
  'AVANTE', // Avante
  'CIDADANIA', // Cidadania
  'NOVO', // Partido Novo
  'Pátria', // Partido Patriota
];

/**
 * Brazilian states (UF) with their proportional representation
 * Proportions based on approximate chamber representation
 */
const UF_DISTRIBUTION = [
  { uf: 'SP', weight: 70 },   // São Paulo - largest representation
  { uf: 'MG', weight: 37 },   // Minas Gerais
  { uf: 'RJ', weight: 46 },   // Rio de Janeiro
  { uf: 'BA', weight: 39 },   // Bahia
  { uf: 'PR', weight: 30 },   // Paraná
  { uf: 'RS', weight: 35 },   // Rio Grande do Sul
  { uf: 'PE', weight: 25 },   // Pernambuco
  { uf: 'CE', weight: 22 },   // Ceará
  { uf: 'PA', weight: 18 },   // Pará
  { uf: 'GO', weight: 17 },   // Goiás
  { uf: 'PB', weight: 12 },   // Paraíba
  { uf: 'SC', weight: 16 },   // Santa Catarina
  { uf: 'MA', weight: 18 },   // Maranhão
  { uf: 'ES', weight: 10 },   // Espírito Santo
  { uf: 'PI', weight: 10 },   // Piauí
  { uf: 'AL', weight: 9 },    // Alagoas
  { uf: 'RN', weight: 8 },    // Rio Grande do Norte
  { uf: 'MT', weight: 8 },    // Mato Grosso
  { uf: 'MS', weight: 8 },    // Mato Grosso do Sul
  { uf: 'DF', weight: 8 },    // Distrito Federal
  { uf: 'AC', weight: 4 },    // Acre
  { uf: 'AM', weight: 8 },    // Amazonas
  { uf: 'AP', weight: 2 },    // Amapá
  { uf: 'RO', weight: 4 },    // Rondônia
  { uf: 'RR', weight: 2 },    // Roraima
  { uf: 'TO', weight: 4 },    // Tocantins
];

/**
 * Câmara dos Deputados federal photo URL base
 * Format: https://www.camara.leg.br/internet/deputado/bandep/{ID}.jpg
 */
const CAMERA_PHOTO_BASE_URL = 'https://www.camara.leg.br/internet/deputado/bandep';

/**
 * Select a random party from the available parties
 */
function selectRandomParty(): string {
  return POLITICAL_PARTIES[Math.floor(Math.random() * POLITICAL_PARTIES.length)];
}

/**
 * Select a random state (UF) with proportional distribution
 */
function selectRandomUF(): string {
  const totalWeight = UF_DISTRIBUTION.reduce((sum, item) => sum + item.weight, 0);
  let random = Math.random() * totalWeight;

  for (const distribution of UF_DISTRIBUTION) {
    random -= distribution.weight;
    if (random <= 0) {
      return distribution.uf;
    }
  }

  return 'SP'; // fallback
}

/**
 * Generate realistic mock deputy data
 * Generates 513 deputies to match Brazilian Chamber size
 *
 * @param count Number of deputies to generate (default: 513)
 * @returns Array of mock Deputado objects
 */
export function generateDeputados(count: number = 513): Deputado[] {
  const deputies: Deputado[] = [];

  for (let i = 1; i <= count; i++) {
    const nameIndex = (i - 1) % DEPUTY_NAMES.length;
    const deputyName = `${DEPUTY_NAMES[nameIndex]} ${Math.floor(i / DEPUTY_NAMES.length)}`.trim();

    const deputado: Deputado = {
      id: i,
      nome: deputyName,
      partido: selectRandomParty(),
      uf: selectRandomUF(),
      foto_url: `${CAMERA_PHOTO_BASE_URL}/${i}.jpg`,
      // Some deputies may not have email in mock data
      email: Math.random() > 0.3 ? `deputado${i}@camara.leg.br` : undefined,
    };

    deputies.push(deputado);
  }

  return deputies;
}

/**
 * Get a single deputy by ID
 *
 * @param deputados Array of deputies
 * @param id Deputy ID
 * @returns Deputy if found, undefined otherwise
 */
export function getDeputadoById(deputados: Deputado[], id: number): Deputado | undefined {
  return deputados.find((d) => d.id === id);
}

/**
 * Filter deputies by name (case-insensitive substring match)
 *
 * @param deputados Array of deputies
 * @param nome Name to search
 * @returns Filtered array of deputies
 */
export function filterDeputadosByNome(deputados: Deputado[], nome: string): Deputado[] {
  const lowerNome = nome.toLowerCase();
  return deputados.filter((d) => d.nome.toLowerCase().includes(lowerNome));
}

/**
 * Filter deputies by party
 *
 * @param deputados Array of deputies
 * @param partido Party abbreviation
 * @returns Filtered array of deputies
 */
export function filterDeputadosByPartido(deputados: Deputado[], partido: string): Deputado[] {
  return deputados.filter((d) => d.partido === partido);
}

/**
 * Filter deputies by state (UF)
 *
 * @param deputados Array of deputies
 * @param uf State abbreviation
 * @returns Filtered array of deputies
 */
export function filterDeputadosByUF(deputados: Deputado[], uf: string): Deputado[] {
  return deputados.filter((d) => d.uf === uf);
}
