import { describe, it, expect } from 'vitest';
import { estimateRecipeCalories, getCalorieLabel } from '../utils/calorieEstimator';

describe('calorieEstimator', () => {
  it('getCalorieLabel doğru etiket döner', () => {
    expect(getCalorieLabel(300)).toBe('Düşük');
    expect(getCalorieLabel(500)).toBe('Orta');
    expect(getCalorieLabel(800)).toBe('Yüksek');
  });

  it('estimateRecipeCalories malzeme listesinden tahmin yapar', () => {
    const calories = estimateRecipeCalories("['tavuk', 'domates', 'soğan']");
    expect(calories).toBeGreaterThan(0);
  });
});
