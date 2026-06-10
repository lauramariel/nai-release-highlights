import { defineCollection, z } from 'astro:content';

const releases = defineCollection({
  type: 'content',
  schema: z.object({
    version: z.string(),
    release_date: z.coerce.date(),
    summary: z.string(),
    features: z.array(z.object({
      title: z.string(),
      description: z.string(),
      category: z.string(),
    })).default([]),
    fixed_issues: z.array(z.object({
      title: z.string(),
      description: z.string(),
    })).default([]),
    known_issues: z.array(z.object({
      title: z.string(),
      description: z.string(),
      workaround: z.string().optional(),
    })).default([]),
  }),
});

export const collections = { releases };
