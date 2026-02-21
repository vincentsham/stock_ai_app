variable "db_password" {
  type      = string
  sensitive = true
}

variable "openai_api_key" {
  type      = string
  sensitive = true
}

variable "gemini_api_key" {
  type      = string
  sensitive = true
}

variable "tavily_api_key" {
  type      = string
  sensitive = true
}

variable "ninja_api_key" {
  type      = string
  sensitive = true
}

variable "fmp_api_key" {
  type      = string
  sensitive = true
}

variable "finnhub_api_key" {
  type      = string
  sensitive = true
}

variable "db_username" {
  type      = string
  default   = "db_admin"
  sensitive = true
}

variable "db_name" {
  type    = string
  default = "stock_ai_db"
}