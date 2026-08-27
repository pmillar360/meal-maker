import { RecipeAvailabilitySummary } from './TypeService';

export type RecipeRankingMode = 'balanced' | 'closest' | 'mostComplete';

const toBoundedFraction = (value: number, max: number) => {
  if (max <= 0) return 0;
  return Math.min(value, max) / max;
};

const getCoverage = (summary: RecipeAvailabilitySummary) => {
  if (summary.total_ingredients <= 0) return 0;
  return summary.available_ingredients / summary.total_ingredients;
};

const getAvailabilityBucket = (summary: RecipeAvailabilitySummary) => {
  if (summary.missing_ingredients === 0) {
    return 0; // Ready now
  }

  if (summary.missing_ingredients <= 3 || getCoverage(summary) >= 0.65) {
    return 1; // Nearly there
  }

  return 2; // Longer stretch
};

const getBalancedAvailabilityScore = (summary: RecipeAvailabilitySummary) => {
  const coverage = getCoverage(summary);
  const availableScore = toBoundedFraction(summary.available_ingredients, 8);
  const missingPenalty = toBoundedFraction(summary.missing_ingredients, 8);
  const sizeBonus = toBoundedFraction(summary.total_ingredients, 12);

  return (
    0.5 * coverage +
    0.3 * availableScore -
    0.15 * missingPenalty +
    0.05 * sizeBonus
  );
};

const getClosestAvailabilityScore = (summary: RecipeAvailabilitySummary) => {
  const coverage = getCoverage(summary);
  const availableScore = toBoundedFraction(summary.available_ingredients, 10);
  const missingPenalty = toBoundedFraction(summary.missing_ingredients, 10);

  return (
    0.55 * coverage +
    0.35 * availableScore -
    0.25 * missingPenalty
  );
};

const getMostCompleteAvailabilityScore = (summary: RecipeAvailabilitySummary) => {
  const coverage = getCoverage(summary);
  const availableScore = toBoundedFraction(summary.available_ingredients, 12);
  const sizeBonus = toBoundedFraction(summary.total_ingredients, 16);
  const missingPenalty = toBoundedFraction(summary.missing_ingredients, 12);

  return (
    0.35 * coverage +
    0.5 * availableScore +
    0.2 * sizeBonus -
    0.1 * missingPenalty
  );
};

const getRankScore = (
  summary: RecipeAvailabilitySummary,
  mode: RecipeRankingMode
) => {
  if (mode === 'closest') {
    return getClosestAvailabilityScore(summary);
  }

  if (mode === 'mostComplete') {
    return getMostCompleteAvailabilityScore(summary);
  }

  return getBalancedAvailabilityScore(summary);
};

export const compareRecipeAvailability = (
  left: RecipeAvailabilitySummary,
  right: RecipeAvailabilitySummary,
  mode: RecipeRankingMode = 'balanced'
) => {
  if (mode === 'balanced') {
    const leftBucket = getAvailabilityBucket(left);
    const rightBucket = getAvailabilityBucket(right);

    if (leftBucket !== rightBucket) {
      return leftBucket - rightBucket;
    }
  }

  const leftScore = getRankScore(left, mode);
  const rightScore = getRankScore(right, mode);

  if (leftScore !== rightScore) {
    return rightScore - leftScore;
  }

  if (left.missing_ingredients !== right.missing_ingredients) {
    return left.missing_ingredients - right.missing_ingredients;
  }

  if (left.available_ingredients !== right.available_ingredients) {
    return right.available_ingredients - left.available_ingredients;
  }

  return right.total_ingredients - left.total_ingredients;
};

export const sortByAvailableIngredientsDesc = (
  left: RecipeAvailabilitySummary,
  right: RecipeAvailabilitySummary
) => compareRecipeAvailability(left, right, 'balanced');

export const rankRecipeAvailability = (
  summaries: RecipeAvailabilitySummary[],
  mode: RecipeRankingMode = 'balanced'
) => [...summaries].sort((left, right) => compareRecipeAvailability(left, right, mode));
