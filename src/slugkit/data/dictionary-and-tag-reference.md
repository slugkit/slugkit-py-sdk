# SlugKit Dictionary & Tag Reference

**Complete guide to SlugKit's word dictionaries, content tags, and filtering strategies.**

## Word Dictionaries Overview

SlugKit provides 6 main word dictionaries with rich tagging for precise content control:

```
📊 Use dictionary_info() to see current word counts
📋 Use dictionary_tags() to see all available tags
```

### Available Dictionaries

| Dictionary | Count | Description | Examples |
|------------|-------|-------------|----------|
| **adjective** | ~17,082 | Descriptive words | fast, brilliant, secure, broken |
| **noun** | ~41,469 | Objects, concepts, people | server, database, user, platform |
| **verb** | ~8,405 | Action words | deploy, connect, analyze, configure |
| **adverb** | ~3,619 | Manner descriptors | quickly, efficiently, securely |
| **domain** | ~9,183 | Internet domains | com, org, tech, dev, aws |
| **shell** | ~2,137 | Command-line tools | git, docker, npm, curl, ssh |

## Tag System

Tags allow precise filtering of word content by theme, emotion, appropriateness, and domain.

### Emotional Tags

Control the emotional tone of generated content:

#### Adjectives & Adverbs
```
+pos    → Positive: amazing, brilliant, secure, fast
+neg    → Negative: broken, failed, slow, unstable  
+emo    → Emotional: passionate, thrilling, devastating
+neut   → Neutral: standard, regular, basic, normal
+det    → Detached: systematic, mechanical, procedural
+obj    → Objective: stable, logical, factual, direct
```

#### Nouns & Verbs
```
+pos    → Positive concepts: success, achievement, growth
+neg    → Negative concepts: failure, error, breakdown
+emo    → Emotional concepts: passion, excitement, fear
+neut   → Neutral concepts: system, process, method
+det    → Detached concepts: mechanism, procedure, protocol
+obj    → Objective concepts: data, analysis, structure
```

### Content Appropriateness

Control content suitability for different audiences:

```
+nsfw   → Not Safe For Work (opt-in only): explicit content
-nsfw   → Exclude NSFW content (recommended for production)
+obj    → Objective, professional tone
```

**⚠️ NSFW Content**: NSFW-tagged words are opt-in only. Use `+nsfw` explicitly to include them.

### Object Categories (Nouns)

#### Main Categories
```
+object   → Physical objects: server, desk, car, building (18,861 words)
+artifact → Human-made items: software, document, tool (6,787 words)
+device   → Electronic devices: phone, laptop, router (1,673 words)
+machine  → Mechanical devices: engine, motor, generator (141 words)
+person   → People: manager, developer, user, admin (6,273 words)
+animal   → Animals: dolphin, eagle, tiger, wolf (2,437 words)
```

#### Specialized Categories
```
+activity → Actions/processes: deployment, analysis, testing (2,663 words)
+event    → Occurrences: meeting, launch, update (6,644 words)
+location → Places: office, warehouse, factory, home (882 words)
+building → Structures: office, warehouse, factory, home (231 words)
+vehicle  → Transportation: car, truck, plane, ship (198 words)
+substance → Materials: metal, wood, plastic, liquid (2,407 words)
+material → Raw materials: steel, concrete, fabric (1,856 words)
+food     → Food items: pizza, coffee, bread, salad (826 words)
+drink    → Beverages: coffee, tea, water, juice (23 words)
+plant    → Flora: tree, flower, grass, leaf (25 words)
+currency → Money/financial: dollar, euro, bitcoin, cash (57 words)
+fantasy  → Fantasy elements: dragon, magic, wizard, quest (59 words)
```

#### Abstract Categories
```
+content  → Information content: article, document, data (1,446 words)
+information → Data/knowledge: facts, statistics, records (133 words)
+concept  → Abstract ideas: theory, principle, philosophy (203 words)
+idea     → Thoughts: concept, notion, plan, strategy (380 words)
+emotion  → Feelings: joy, anger, fear, excitement (229 words)
+feeling  → Sensations: warmth, pain, comfort, tension (683 words)
+music    → Musical terms: song, rhythm, melody, beat (255 words)
+art      → Artistic concepts: painting, sculpture, design (63 words)
+action   → Actions: deployment, execution, processing (1,693 words)
+creation → Created things: product, design, solution (492 words)
+unit     → Measurement units: meter, kilogram, byte (528 words)
+number   → Numeric concepts: count, total, percentage (239 words)
```

#### Technical Categories
```
+chemical → Chemicals: compound, element, solution (904 words)
+drug     → Pharmaceuticals: medicine, treatment, dose (644 words)
+surface  → Surfaces: interface, boundary, layer (128 words)
+furniture → Furniture: desk, chair, table, shelf (107 words)
+situation → Circumstances: context, scenario, case (78 words)
+state    → Conditions: status, mode, phase (4 words)
+shop     → Commercial places: store, market, outlet (38 words)
```

### Action Categories (Verbs)

#### Primary Actions
```
+change   → Transformation: convert, modify, update, evolve (2,583 words)
+act      → Physical actions: run, jump, build, move (1,246 words)
+travel   → Movement: navigate, journey, migrate, explore (463 words)
```

#### State & Possession
```
+be       → State of being: exist, remain, become, stay (215 words)
+have     → Possession: own, contain, include, hold (119 words)
```

#### Creation & Destruction
```
+make     → Creation: build, generate, create, produce (5 words)
+create   → Creative actions: design, compose, invent (2 words)
+become   → Transformation into state: turn, grow, develop (4 words)
+destroy  → Destructive actions: delete, remove, break (29 words)
+take     → Taking actions: grab, acquire, capture (1 word)
+give     → Giving actions: provide, share, offer (1 word)
+imagine  → Mental actions: think, dream, visualize (20 words)
```

### Domain Categories

#### Domains by Type
```
+com      → Commercial domains (.com sites) (989 words)
+org      → Organization domains (.org sites) (175 words)
+net      → Network domains (.net sites) (225 words)
+tld      → Top-level domains: com, org, net, gov (1,281 words)
+sld      → Second-level domains: company, product names (4,853 words)
+sub      → Subdomain parts: www, api, blog, shop (3,049 words)
```

#### Modern Tech Domains
```
+io       → Tech domains (.io sites) (91 words)
+dev      → Developer domains (.dev sites) (62 words)
+app      → Application domains (.app sites) (49 words)
+cloud    → Cloud domains (.cloud sites) (65 words)
+tech     → Technology domains (.tech sites) (2 words)
```

#### Regional Domains
```
+us       → United States domains (.us) (245 words)
+uk       → United Kingdom domains (.uk) (43 words)
+de       → German domains (.de) (76 words)
+jp       → Japanese domains (.jp) (1,890 words)
+au       → Australian domains (.au) (35 words)
+ca       → Canadian domains (.ca) (22 words)
+fr       → French domains (.fr) (33 words)
```

## Tag Filtering Strategies

### Include Multiple Tags
```
{noun:+device+object}         → Technical objects: server, router, database
{adjective:+pos+obj}          → Positive objective terms: excellent, stable, reliable
{verb:+change+act}            → Active transformation verbs: modify, improve, enhance
```

### Exclude Unwanted Content
```
{adjective:-neg-nsfw}         → No negative or NSFW words
{noun:+device-animal}         → Tech devices, but no animals
{verb:-destroy-neg}           → No destructive or negative actions
```

### Complex Combinations
```
{adjective:+pos+obj-emo<8}    → Positive objective adjectives, not emotional, max 7 chars
{noun:+object+device-nsfw>=4} → Tech objects, family-friendly, min 4 chars
{verb:+change+act-destroy}    → Change-related action verbs, not destructive
```

## Content Strategy by Use Case

### Professional/Business Content
```
# Recommended tags
{adjective:+pos+obj-nsfw}     → professional, positive, appropriate
{noun:+device+artifact-nsfw}  → business/tech focused, clean
{verb:+change+act-destroy}    → constructive actions only

# Example pattern
"{adjective:+pos+obj} {noun:+device} {verb:+change} {adverb:+pos}"
→ "secure platform deploys efficiently"
```

### Family-Friendly Content
```
# Always exclude NSFW
{adjective:-nsfw+pos}         → positive, clean adjectives
{noun:+animal+object-nsfw}    → animals and objects, family-safe
{verb:+act+change-destroy-nsfw} → constructive, clean verbs

# Example pattern  
"{adjective:+pos-nsfw} {noun:+animal-nsfw} {verb:+act-nsfw}"
→ "happy dolphin jumps"
```

### Technical Documentation
```
# Focus on objective, technical terms
{adjective:+obj-emo}          → objective, unemotional
{noun:+device+object+artifact} → tech equipment and systems  
{verb:+change+act}            → technical operations

# Example pattern
"{verb:+change} {adjective:+obj} {noun:+device}"
→ "configure secure server"
```

### Creative/Marketing Content
```
# Allow emotional, positive language
{adjective:+pos+emo}          → exciting, emotional positivity
{noun:+concept+idea+object}   → broad creative concepts
{verb:+create+act+change}     → dynamic, creative actions

# Example pattern
"The {adjective:+pos+emo} {noun:+concept} will {verb:+create} {adjective:+pos} {noun:+object}"
→ "The amazing platform will generate brilliant solutions"
```

### Gaming/Fantasy Content
```
# Include fantasy and creative elements
{adjective:+pos+emo}          → dramatic, positive descriptors
{noun:+fantasy+animal+person} → fantasy characters and creatures
{verb:+act+imagine+destroy}   → dramatic fantasy actions

# Example pattern
"{adjective:+pos} {noun:+fantasy} {verb:+act} the {adjective:+neg} {noun:+fantasy}"
→ "Mighty wizard defeats the evil dragon"
```

## Language Support

### Current Language Tags
```
@en    → English (default)
@es    → Spanish (if available)
@fr    → French (if available)  
@de    → German (if available)
```

**Note**: Language support varies by dictionary. Use `dictionary_info()` to check availability.

### Usage Examples
```
{adjective@en}-{noun@en}      → Force English words
{noun@es} and {noun@fr}       → Mix Spanish and French
{adjective}-{noun}[@de]       → German words globally
```

## Best Practices

### Production Applications
1. **Always exclude NSFW**: Use `-nsfw` in all patterns
2. **Use positive/neutral tone**: `+pos` or `+neut` for user-facing content
3. **Be specific with categories**: `+device` for technical contexts, `+person` for user references
4. **Control length**: Use length constraints for UI/database limits

### Testing & Development  
1. **Use diverse tags**: Test with different emotional tones
2. **Include edge cases**: Try `+neg` content for error scenarios
3. **Validate thoroughly**: Check capacity impact of tag combinations
4. **Consider caching**: Tag filtering can impact performance

### Content Strategy
1. **Match your audience**: Family-friendly vs. professional vs. technical
2. **Consistent theming**: Use global settings for pattern-wide consistency
3. **Cultural sensitivity**: Consider international audiences with language tags
4. **Brand alignment**: Choose tags that match your brand voice

## Advanced Tag Techniques

### Tag Hierarchies
Some tags work better together:
```
+device+obj      → Technical devices, objective (great for APIs)
+pos+person      → Positive people language (user-friendly)
+change+act      → Dynamic transformation language
+animal+fantasy  → Mythical creatures and magical animals
```

### Performance Considerations
```
# More specific = better performance
{noun:+device+object<8}       → Highly filtered, fast
{noun}                        → Broad selection, slower with large sets
{noun:+animal+fantasy+emo}    → Multiple tags, moderate performance
```

### Capacity Impact
```
# Check capacity before using
validate_pattern("{noun:+device}")   → Smaller subset (1,673 words)
validate_pattern("{noun}")           → Full dictionary (41,469 words)
validate_pattern("{noun:+fantasy}")  → Very specific (59 words)
```

## Real Examples with Actual Tags

### ✅ Working Examples
```
// Valid adjective tags
{adjective:+pos}    → positive words (710 available)
{adjective:+obj}    → objective words (8,382 available)
{adjective:+neg}    → negative words (1,395 available)

// Valid noun tags  
{noun:+device}      → devices (1,673 available)
{noun:+person}      → people (6,273 available)
{noun:+animal}      → animals (2,437 available)
{noun:+object}      → objects (18,861 available)

// Valid verb tags
{verb:+change}      → change actions (2,583 available)
{verb:+act}         → general actions (1,246 available)

// Valid domain tags
{domain:+com}       → .com domains (989 available)
{domain:+tld}       → top-level domains (1,281 available)
```

### ❌ Common Invalid Tags
```
// These DON'T exist - will cause errors
{adjective:+tech}     → ❌ No tech tag for adjectives
{noun:+tech}          → ❌ No tech tag for nouns  
{adjective:+business} → ❌ No business tag
{verb:+tech}          → ❌ No tech tag for verbs
{noun:+professional}  → ❌ No professional tag
{adjective:+security} → ❌ No security tag
```

## Tag Availability Summary

### Adjectives (7 tags total)
- `det` (14,138 words) - Detached/analytical
- `obj` (8,382 words) - Objective  
- `neut` (6,595 words) - Neutral
- `emo` (2,944 words) - Emotional
- `neg` (1,395 words) - Negative
- `pos` (710 words) - Positive
- `nsfw` (35 words) - Not safe for work

### Nouns (44 tags total)
Most useful:
- `object` (18,861) - General objects
- `det` (39,391) - Detached concepts
- `obj` (26,812) - Objective things
- `artifact` (6,787) - Human-made items
- `event` (6,644) - Events/occurrences
- `person` (6,273) - People and roles
- `activity` (2,663) - Activities
- `animal` (2,437) - Animals
- `substance` (2,407) - Materials
- `material` (1,856) - Raw materials
- `action` (1,693) - Actions
- `device` (1,673) - Electronic devices
- `content` (1,446) - Information content

### Verbs (17 tags total)
Most useful:
- `det` (8,172) - Detached actions
- `obj` (5,689) - Objective actions  
- `neut` (2,597) - Neutral actions
- `change` (2,583) - Change actions
- `act` (1,246) - Physical actions
- `travel` (463) - Movement
- `emo` (233) - Emotional actions
- `be` (215) - State of being

### Domains (195+ tags)
Including country codes, TLDs, and special categories like `com`, `org`, `tld`, `dev`, `io`, etc.

## Pattern Testing Examples

Test these working patterns:

```
// Simple professional patterns
validate_pattern("{adjective:+pos}-{noun:+device}")
forge("{adjective:+pos}-{noun:+device}", count=3)
→ ["amazing-server", "brilliant-database", "excellent-platform"]

// User-friendly IDs  
validate_pattern("{adjective:+pos}-{noun:+animal}-{number:3d}")
forge("{adjective:+pos}-{noun:+animal}-{number:3d}", count=3)
→ ["happy-dolphin-142", "smart-eagle-738", "bright-tiger-395"]

// Technical naming
validate_pattern("{noun:+device}-{adjective:+obj}-{number:2x}")
forge("{noun:+device}-{adjective:+obj}-{number:2x}", count=3)
→ ["server-stable-a3", "database-secure-f7", "router-direct-2c"]

// Domain examples
validate_pattern("{adjective:+pos}.{domain:+tld}")
forge("{adjective:+pos}.{domain:+tld}", count=3)
→ ["amazing.com", "brilliant.org", "excellent.net"]
```

---

**💡 Key Takeaways:**
- **Always use `dictionary_tags()` first** to see what's actually available
- **Most "expected" tags don't exist** - SlugKit has a specific, limited set
- **Focus on emotional tags** (`+pos`, `+neg`, `+obj`) and category tags (`+device`, `+person`, `+animal`)
- **Test patterns before using** with `validate_pattern()` 
- **Start simple** and add constraints gradually
- **The documentation had many invalid examples** - always verify against the actual API

Use `dictionary_info()` and `dictionary_tags()` as your source of truth, not documentation examples!
