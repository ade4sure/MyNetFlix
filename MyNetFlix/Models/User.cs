namespace MyNetFlix.Models
{
    public class User
    {
        public required string Email { get; set; }
        public required string Password { get; set; }
        
    }
    
    public class Movie
    {
        public required string Title { get; set; }
        public required string Producer { get; set; }
        public required string Category { get; set; }
        public required string Filename { get; set; }
        public required int Year { get; set; }
    }

    public  class MoviesDTO
    {
        public IEnumerable<Movie> Movies { get; set; }
        public List<string> Categories { get; set; }
    }
}
