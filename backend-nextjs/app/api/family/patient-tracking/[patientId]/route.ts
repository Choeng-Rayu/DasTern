import { successResponse, errorResponse } from "@/lib/utils/response";
import { query } from '@/lib/db'
import { NextRequest } from "next/server";
import { withDoctorAuth, withFamilyAuth } from "@/lib/middleware/auth";
import { JwtPayload } from '@/lib/types/auth.types';
import { error } from "console";

async function getHandler(req: NextRequest, auth: JwtPayload){
    try {
        const result = await query(
            ` SELECT status 
            FROM family_patient_relationships 
            WHERE family_id = $1 
            AND patient_id = $2 
            AND status = 'approved';
            `, [auth.userId]
        );
        if (result.rowCount == 0) return errorResponse("Faild to view paient prescription", 404);

        return successResponse("status: successfully");
    } catch (error)
    {
        console.error("Error", error);
        return errorResponse('There is an error', 500)
    }
}

export const POST = withFamilyAuth(getHandler);