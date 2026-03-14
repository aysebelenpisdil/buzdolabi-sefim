import { describe, it, expect } from 'vitest';
import { parseIngredientList } from '../utils/helpers';

describe('parseIngredientList', () => {
  it('boş string boş dizi döner', () => {
    expect(parseIngredientList('')).toEqual([]);
  });

  it('JSON array string parse eder', () => {
    const input = "['domates', 'soğan', 'biber']";
    expect(parseIngredientList(input)).toContain('domates');
    expect(parseIngredientList(input)).toContain('soğan');
    expect(parseIngredientList(input)).toContain('biber');
  });
});
