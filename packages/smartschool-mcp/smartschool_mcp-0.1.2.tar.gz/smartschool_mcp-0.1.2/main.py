"""
Smartschool MCP Server
Provides tools to interact with Smartschool API for courses, results and tasks.
"""

from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from smartschool import Courses, EnvCredentials, Smartschool, Results, ResultDetail, FutureTasks, MessageHeaders, Message, BoxType

# Initialize MCP server and Smartschool session
mcp = FastMCP("Smartschool MCP")
session = Smartschool(EnvCredentials())


def _safe_get_teacher_names(teachers, use_last_name: bool = True) -> List[str]:
    """Safely extract teacher names from teacher objects."""
    if not teachers:
        return []
    
    try:
        if use_last_name:
            return [teacher.name.startingWithLastName for teacher in teachers]
        else:
            return [teacher.name.startingWithFirstName for teacher in teachers]
    except (AttributeError, IndexError):
        return []


def _safe_format_date(date_obj) -> Optional[str]:
    """Safely format date objects to string."""
    try:
        return date_obj.strftime('%Y-%m-%d') if date_obj else None
    except (AttributeError, ValueError):
        return None


@mcp.tool()
def get_courses() -> List[Dict[str, Any]]:
    """
    Retrieve all available courses with their teachers.
    
    Returns:
        List of courses with name and teacher information.
    """
    try:
        courses = Courses(session)
        courses_list = []
        
        for course in courses:
            teacher_names = _safe_get_teacher_names(course.teachers, use_last_name=True)
            courses_list.append({
                "name": course.name,
                "teachers": teacher_names,
            })
        
        return courses_list
    
    except Exception as e:
        return [{"error": f"Failed to retrieve courses: {str(e)}"}]


@mcp.tool()
def get_results(limit: int = 15, offset: int = 0, course_filter: Optional[str] = None, include_details: bool = True) -> Dict[str, Any]:
    """
    Retrieve student results/grades with detailed information.
    
    Args:
        limit: Maximum number of results to return (default: 15)
        offset: Number of results to skip from the beginning (default: 0)
        course_filter: Filter results by course name (partial match, case-insensitive)
        include_details: Whether to fetch detailed info (teacher, average, median) - saves API calls if False
    
    Returns:
        Dictionary with results list and pagination info.
        
    Examples:
        - get_results() -> First 15 results with details
        - get_results(course_filter="Math") -> Results from courses containing "Math"
        - get_results(include_details=False) -> Basic info only, faster response
    """
    try:
        results = Results(session)
        all_results = list(results)
        
        # Apply course filtering
        if course_filter:
            filtered_results = []
            for result in all_results:
                course_name = result.courses[0].name if result.courses else ""
                if course_filter.lower() in course_name.lower():
                    filtered_results.append(result)
            all_results = filtered_results
        
        # Apply pagination
        end_index = offset + limit
        paginated_results = all_results[offset:end_index]
        
        results_list = []
        
        for result in paginated_results:
            # Basic result information
            result_data = {
                "course": result.courses[0].name if result.courses else "Unknown",
                "assignment": result.name or "Unknown Assignment",
                "score_description": getattr(result.graphic, 'description', 'N/A'),
                "score_value": getattr(result.graphic, 'value', None),
                "date": _safe_format_date(result.date),
                "published_date": _safe_format_date(result.availabilityDate),
                "counts": getattr(result, 'doesCount', None),
                "feedback": result.feedback[0].text if result.feedback else "",
            }
            
            # Only fetch detailed information if requested
            if include_details:
                result_data.update({
                    "teacher": None,
                    "average": None,
                    "median": None
                })
                
                # Try to get detailed information
                try:
                    details = ResultDetail(session, result_id=result.identifier)
                    detail = details.get()
                    
                    # Extract teacher information
                    if hasattr(detail, 'details') and detail.details.teachers:
                        teacher_names = _safe_get_teacher_names(detail.details.teachers, use_last_name=False)
                        result_data["teacher"] = teacher_names[0] if teacher_names else None
                    
                    # Extract statistical information
                    if (hasattr(detail, 'details') and 
                        hasattr(detail.details, 'centralTendencies') and 
                        detail.details.centralTendencies):
                        
                        tendencies = detail.details.centralTendencies
                        
                        if len(tendencies) > 0 and hasattr(tendencies[0], 'graphic'):
                            result_data["average"] = {
                                "description": getattr(tendencies[0].graphic, 'description', 'N/A'),
                                "value": getattr(tendencies[0].graphic, 'value', None)
                            }
                        
                        if len(tendencies) > 1 and hasattr(tendencies[1], 'graphic'):
                            result_data["median"] = {
                                "description": getattr(tendencies[1].graphic, 'description', 'N/A'),
                                "value": getattr(tendencies[1].graphic, 'value', None)
                            }
                
                except Exception:
                    # Keep default None values for detailed information
                    pass
            
            results_list.append(result_data)
        
        # Add metadata about pagination and filtering
        total_results = len(all_results)
        return {
            "results": results_list,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_results,
                "returned": len(results_list),
                "has_more": end_index < total_results
            },
            "filters": {
                "course_filter": course_filter,
                "include_details": include_details
            }
        }
    
    except Exception as e:
        return {"error": f"Failed to retrieve results: {str(e)}"}


@mcp.tool()
def get_future_tasks() -> Dict[str, Any]:
    """
    Retrieve upcoming assignments and tasks.
    
    Returns:
        Dictionary with future tasks organized by date and course.
    """
    try:
        future_tasks = FutureTasks(session)
        tasks_data = []
        
        for day in future_tasks:
            day_data = {
                "date": _safe_format_date(day.date),
                "courses": []
            }
            
            for course in day.courses:
                course_data = {
                    "name": course.name if hasattr(course, 'name') else "Unknown Course",
                    "tasks": []
                }
                
                # Extract tasks from the course
                if hasattr(course, 'items') and hasattr(course.items, 'tasks'):
                    for task in course.items.tasks:
                        task_data = {
                            "label": getattr(task, 'label', 'N/A'),
                            "description": getattr(task, 'description', 'N/A')
                        }
                        course_data["tasks"].append(task_data)
                
                # Only add course if it has tasks
                if course_data["tasks"]:
                    day_data["courses"].append(course_data)
            
            # Only add day if it has courses with tasks
            if day_data["courses"]:
                tasks_data.append(day_data)
        
        return {
            "future_tasks": tasks_data,
            "total_days": len(tasks_data),
            "total_tasks": sum(len(task) for day in tasks_data for course in day["courses"] for task in course["tasks"])
        }
    
    except Exception as e:
        return {"error": f"Failed to retrieve future tasks: {str(e)}"}


@mcp.tool()
def get_messages(
    limit: int = 15, 
    offset: int = 0, 
    box_type: str = "INBOX",
    search_query: Optional[str] = None,
    sender_filter: Optional[str] = None,
    include_body: bool = False
) -> Dict[str, Any]:
    """
    Retrieve messages from the specified mailbox with filtering options.
    
    Args:
        limit: Maximum number of messages to return (default: 15)
        offset: Number of messages to skip from the beginning (default: 0)
        box_type: Type of mailbox - "INBOX", "SENT", "DRAFT", etc. (default: "INBOX")
        search_query: Search in subject and body content (case-insensitive)
        sender_filter: Filter messages by sender name (partial match, case-insensitive)
        include_body: Whether to include full message body (default: False for performance)
    
    Returns:
        Dictionary with messages list and pagination info.
        
    Examples:
        - get_messages() -> First 15 inbox messages (headers only)
        - get_messages(search_query="homework") -> Messages containing "homework"
        - get_messages(sender_filter="teacher") -> Messages from senders containing "teacher"
        - get_messages(include_body=True) -> Full messages with body content
    """
    try:
        # Convert string box_type to BoxType enum
        try:
            box_type_enum = getattr(BoxType, box_type.upper())
        except AttributeError:
            box_type_enum = BoxType.INBOX  # Default fallback
        
        # Get message headers
        message_headers = MessageHeaders(session, box_type=box_type_enum)
        all_headers = list(message_headers)
        
        # Apply filtering
        filtered_headers = []
        
        for header in all_headers:
            # Get full message for filtering (we need it for search anyway)
            try:
                full_message = Message(session, header.id).get()
                
                # Apply sender filter
                if sender_filter:
                    sender_name = getattr(full_message, 'from_', '') or ''
                    if sender_filter.lower() not in sender_name.lower():
                        continue
                
                # Apply search query filter
                if search_query:
                    subject = getattr(full_message, 'subject', '') or ''
                    body = getattr(full_message, 'body', '') or ''
                    search_text = f"{subject} {body}".lower()
                    
                    if search_query.lower() not in search_text:
                        continue
                
                # Store the full message with the header for later use
                header._full_message = full_message
                filtered_headers.append(header)
                
            except Exception:
                # If we can't get the full message, skip this header
                continue
        
        # Apply pagination
        end_index = offset + limit
        paginated_headers = filtered_headers[offset:end_index]
        
        messages_list = []
        
        for header in paginated_headers:
            # Use cached full message if available, otherwise fetch it
            if hasattr(header, '_full_message'):
                full_message = header._full_message
            else:
                try:
                    full_message = Message(session, header.id).get()
                except Exception:
                    continue
            
            message_data = {
                "id": getattr(header, 'id', None),
                "from": getattr(full_message, 'from_', 'Unknown Sender'),
                "subject": getattr(full_message, 'subject', 'No Subject'),
                "date": _safe_format_date(getattr(header, 'date', None)),
                "read": getattr(header, 'read', None),
                "priority": getattr(header, 'priority', None),
            }
            
            # Include body only if requested
            if include_body:
                message_data["body"] = getattr(full_message, 'body', '')
            else:
                # Provide a preview of the body (first 100 characters)
                body = getattr(full_message, 'body', '') or ''
                message_data["body_preview"] = body[:100] + "..." if len(body) > 100 else body
            
            messages_list.append(message_data)
        
        # Add metadata about pagination and filtering
        total_messages = len(filtered_headers)
        return {
            "messages": messages_list,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_messages,
                "returned": len(messages_list),
                "has_more": end_index < total_messages
            },
            "filters": {
                "box_type": box_type,
                "search_query": search_query,
                "sender_filter": sender_filter,
                "include_body": include_body
            }
        }
    
    except Exception as e:
        return {"error": f"Failed to retrieve messages: {str(e)}"}


if __name__ == "__main__":
    # Server can be run directly for testing
    print("Smartschool MCP Server initialized")

