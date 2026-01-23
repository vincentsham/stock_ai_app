# Database Schema Documentation

## Schema: ref
**Description**: Stores reference data, lookup tables, and embeddings for normalization and mapping purposes.

### Tables in `ref`
- `analyst_grade_mapping`: Mappings of original analyst grades to normalized values, including embeddings.

## Table: ref.analyst_grade_mapping
**Schema**: `ref`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| grade_original  | TEXT                       | NO          | YES*        | Original grade string                    |
| grade_normalized| TEXT                       | NO          |             | Normalized grade string                  |
| grade_value     | SMALLINT                   | NO          |             | Numerical value of the grade             |
| embedding       | VECTOR(1536)               | NO          |             | Embedding vector of the grade            |
| embedding_model | TEXT                       | NO          | YES*        | Model used for the embedding             |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

*\*Composite Primary Key: (grade_original, embedding_model)*
